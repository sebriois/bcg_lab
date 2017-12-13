# coding: utf-8
from datetime import datetime
from urllib.parse import parse_qsl
from decimal import Decimal
import xlwt
import json

from django.shortcuts import get_object_or_404, render, redirect
from django.conf import settings
from django.db.models.query import Q
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse
from django.urls import reverse
from django.utils import timezone
from elasticsearch import Elasticsearch

from provider.models import Provider
from product.models import Product
from product.forms import ProductForm, ProductFilterForm, EditListForm
from utils.request_messages import info_msg


def autocomplete(request):
    q = request.GET.get('query', '')
    
    suggestions = list(set(Product.objects.filter(name__icontains = q).only('name').values_list('name', flat = True)))
    suggestions.sort()
    
    output_data = {
        'query': q,
        'suggestions': suggestions
    }
    
    return HttpResponse(json.dumps(output_data))


def _elastic_search(query_dict):
    es = Elasticsearch()
    query = {
      "query": {
        "filtered": {
          "query": {
            "query_string": {
              "query": query_dict['q']
            }
          }
        }
      },
      "fields": [
        "reference",
        "nomenclature",
        "provider",
        "offer_nb",
        "origin",
        "name",
        "category"
      ],
      "from": 50 * (int(query_dict.get("page", 1)) - 1),
      "size": 50,
      "sort": {
        "_score": {
          "order": "desc"
        }
      }
    }
    res = es.search(index = settings.SITE_NAME.lower(), body = query, filter_path=['hits.total', 'hits.hits._id'])
    product_list = Product.objects.filter(id__in = [hit['_id'] for hit in res['hits']['hits']])

    return product_list, res['hits']['total']


def _django_search(query_dict):
    form = ProductFilterForm(data = query_dict)
    
    if len(query_dict.keys()) > 1:
        if form.is_valid():
            data = dict()
            for key, value in form.cleaned_data.items():
                if value:
                    data[key] = value

            if 'id__in' in query_dict:
                data['id__in'] = query_dict['id__in'].split(',')
            
            if 'has_expired' in query_dict:
                data['expiry__lt'] = timezone.now()
            
            if 'is_valid' in query_dict:
                data['expiry__gte'] = timezone.now()
            
            Q_obj = Q()
            Q_obj.connector = data.pop("connector")
            Q_obj.children  = data.items()
            
            product_list = Product.objects.filter(Q_obj)
            num_found = product_list.count()
        else:
            product_list = Product.objects.none()
            num_found = 0
    else:
        product_list = Product.objects.none()
        num_found = 0
    
    return product_list, num_found


def _product_search(query_dict):
    if 'q' in query_dict.keys() and query_dict['q'].strip():
        product_list, num_found = _elastic_search(query_dict)
    elif len(query_dict.keys()) > 0:
        product_list, num_found = _django_search(query_dict)
    else:
        product_list = Product.objects.none()
        num_found = 0
    
    return product_list, num_found


@login_required
def index(request):
    query_dict = request.GET.copy()
    
    product_list, num_found = _product_search(query_dict)
    
    if request.user.has_perm("order.custom_view_local_provider") and not request.user.is_superuser:
        if not 'q' in query_dict.keys():
            product_list = Product.objects.filter(provider__is_local = True)
        else:
            product_list = product_list.filter(provider__is_local = True)
        num_found = product_list.count()
        product_count = Product.objects.filter(provider__is_local = True).count()
    else:
        product_count = Product.objects.all().count()
    
    # Pagination
    if 'page' in query_dict:
        current_page = int(query_dict.pop('page')[0])
    else:
        current_page = 1
    
    if not 'q' in query_dict.keys():
        start = (current_page - 1) * settings.PAGINATION_ROWS
        end   = start + settings.PAGINATION_ROWS
        if end > num_found:
            end = num_found
        product_list = product_list[start:end]
    
    return render(request, 'product/index.html', {
        'product_count': product_count,
        'search_count': num_found,
        'filter_form': ProductFilterForm(),
        'q_init': query_dict.get("q",""),
        'products': product_list,
        'current_page': current_page,
        'url_args': query_dict.urlencode(),
    })


@login_required
@transaction.atomic
def item(request, product_id):
    product = get_object_or_404(Product, id = product_id)
    form = ProductForm(instance = product, provider = product.provider)
    url_args = request.GET.urlencode()

    if request.method == 'POST':
        data = request.POST.copy()
        url_args = data.pop('url_args')
        form = ProductForm(instance = product, data = data)
        if form.is_valid():
            if form.has_changed():
                orig_price = product.price
                product = form.save()
                if orig_price != product.price and product.has_expired():
                    product.expiry = datetime.strptime("31/12/%s" % timezone.now().year, "%d/%m/%Y")
                    product.save()
                    
                info_msg(request, u"Produit modifié avec succès.")
            return redirect(reverse('product_index') + '?' + url_args[0])
    
    product_type = ContentType.objects.get_for_model(Product)
    return render(request, 'product/item.html',{
        'product': product,
        'product_type': product_type.id,
        'form': form,
        'url_args': url_args
    })


@login_required
@transaction.atomic
def new(request):
    provider = None
    form = ProductForm()

    if request.method == 'GET':
        provider_id = request.GET.get('provider_id',None)
        if provider_id:
            provider = get_object_or_404(Provider, id = provider_id)
            form = ProductForm(provider = provider)
        elif request.user.has_perm("order.custom_view_local_provider"):
            provider = get_object_or_404(Provider, name = 'MAGASIN', is_local = True)
            form = ProductForm(provider = provider)
    elif request.method == 'POST':
        if 'provider' in request.POST and request.POST['provider']:
            provider = get_object_or_404(Provider, id = request.POST['provider'])
            form = ProductForm(provider = provider, data = request.POST)
        else:
            provider = None
            form = ProductForm(data = request.POST)
        
        if form.is_valid():
            p = form.save()
            if p.provider.reseller:
                p.origin = p.provider.name
                p.provider = p.provider.reseller
                p.save()

            info_msg(request, u"Produit ajouté avec succès.")
            return redirect(reverse('product_index') + "?reference=%s&connector=OR" % p.reference)
    
    return render(request, 'product/new.html', {
        'provider': provider,
        'form': form
    })


@login_required
@transaction.atomic
def delete(request, product_id):
    product = get_object_or_404(Product, id = product_id)
    if request.method == 'GET':
        return render(request, "product/delete.html", {
            'product': product
        })
    elif request.method == 'POST':
        product.delete()
        info_msg(request, u"Produit supprimé avec succès.")
        return redirect('product_index')


@login_required
def export_xls(request):
    product_list, num_found = _product_search(request.GET.copy())
    
    if request.user.has_perm("order.custom_view_local_provider"):
        if num_found == 0:
            product_list = Product.objects.all()
        product_list = product_list.filter(provider__is_local = True)
    
    wb = xlwt.Workbook()
    ws = wb.add_sheet("export")
    
    header = [u"FOURNISSEUR", u"DESIGNATION", u"REFERENCE", u"PRIX", u"CONDITIONNEMENT", 
    u"NOMENCLATURE", u"FOURNISSEUR D'ORIGINE", u"N°OFFRE", u"EXPIRATION", u"MISE A JOUR"]
    for col, title in enumerate(header): ws.write(0, col, title)
    
    row = 1
    
    for product in product_list:
        if product.expiry:
            expiry = product.expiry.strftime("%d/%m/%Y")
        else:
            expiry = u""
        
        ws.write(row, 0, product.provider.name)
        ws.write(row, 1, product.name)
        ws.write(row, 2, product.reference)
        ws.write(row, 3, product.price)
        ws.write(row, 4, product.packaging)
        ws.write(row, 5, product.nomenclature)
        ws.write(row, 6, product.origin)
        ws.write(row, 7, product.offer_nb)
        ws.write(row, 8, expiry)
        ws.write(row, 9, product.last_change.strftime("%d/%m/%Y"))
        row += 1
    
    response = HttpResponse(mimetype="application/ms-excel")
    response['Content-Disposition'] = 'attachment; filename=export_produit.xls'
    response['Content-Type'] = 'application/vnd.ms-excel; charset=utf-8'
    wb.save(response)

    return response

@login_required
@transaction.atomic
def edit_list(request):
    if request.method == 'GET':
        product_list, num_found = _product_search(request.GET.copy())
        
        if request.user.has_perm("order.custom_view_local_provider") and not request.user.is_superuser:
            product_list = product_list.filter(provider__is_local = True)
        
        return render(request, 'product/edit_list.html', {
            'filter_form': ProductFilterForm(),
            'edit_form': EditListForm(),
            'product_list': product_list,
            'url_args': request.GET.urlencode()
        })
    
    if request.method == 'POST':
        form = EditListForm(data = request.POST)
        
        if form.is_valid():
            clean_data = form.cleaned_data
            
            percent_raise = clean_data.get('percent_raise', None)
            category = clean_data.get('category', None)
            sub_category = clean_data.get('sub_category', None)
            nomenclature = clean_data.get('nomenclature', None)
            offer_nb = clean_data.get('offer_nb',None)
            expiry = clean_data.get('expiry',None)
            
            product_ids = map(
                lambda item: int(item.split("_")[1]), 
                filter(
                    lambda key: key.startswith("product_"), 
                    request.POST.keys() 
            )
        )
            
            product_list = Product.objects.filter(id__in = product_ids)
            
            for product in product_list:
                if request.POST['delete_all'] == "on":
                    product.delete()
                    continue
                
                if category: product.category = category
                if sub_category: product.sub_category = sub_category
                if nomenclature: product.nomenclature = nomenclature.strip()
                if percent_raise:
                    product.price = product.price * Decimal(1 + percent_raise / 100)
                if offer_nb: product.offer_nb = offer_nb
                if expiry: product.expiry = expiry
                product.save()
            
            if request.POST['delete_all'] == "on":
                info_msg(request, "Produits supprimés avec succès.")
                return redirect(reverse('product_edit_list') + "?" + request.POST["url_args"])
            else:
                info_msg(request, "Liste de produits mise à jour avec succès.")
                return redirect(reverse('product_edit_list') + "?" + request.POST["url_args"])
        else:
            url_args = dict(parse_qsl(request.POST["url_args"]))
            product_list, filter_form = _product_search(url_args)
            
            return render(request, 'product/edit_list.html', {
                'edit_form': form,
                'product_list': product_list,
                'url_args': request.POST['url_args']
            })
