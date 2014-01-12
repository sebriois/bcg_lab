# coding: utf-8

from datetime import datetime, date
from decimal import Decimal
import urlparse
import xlwt
import json

from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import urlencode
from django.conf import settings
from django.core.urlresolvers import reverse
from django.db.models.query import Q
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse

from provider.models import Provider
from product.models import Product
from product.forms import ProductForm, ProductFilterForm, EditListForm
from order.models import Order, OrderItem
from attachments.models import Attachment

from bcg_lab.constants import *
from utils import *
from solr import Solr

def search(request):   
    query = request.GET.get("q", None)
    facet_query = request.GET.get("fq", '')
    
    if query:
        solr = Solr()
        solr.query({ 
            'q': query,
            'fq': facet_query
        })
        
        suggestion = solr.suggestion()
        
        return render(request, 'product/search.html', {
            'numFound': solr.numFound(),
            'query': query,
            'facet_query': facet_query and facet_query.split(':')[1] or None,
            'facets': solr.facet_fields(),
            'suggestion': suggestion,
            'product_list': Product.objects.filter( id__in = [doc['id'] for doc in solr.docs()] ),
        })
    else:
        return render(request, 'product/search.html', {
            'product_list': Product.objects.none()
        })

def autocomplete(request):
    text_typed = request.GET.get('query', '')
    
    solr = Solr()
    solr.query({
        'q': '*:*',
        'rows': 0,
        'facet': 'true',
        'facet.field': 'product_auto',
        'facet.prefix': text_typed,
    })
    
    results = solr.facet_fields('product_auto')
    
    output_data = {
        'query': text_typed,
        'suggestions': [results[i] for i in xrange(0, len(results), 2)]
    }
    
    return HttpResponse(json.dumps(output_data))


def _solr_search( query_dict ):
    solr = Solr()
    solr.query( query_dict )
    
    product_list = Product.objects.filter( id__in = [doc['id'] for doc in solr.docs()] )
    
    return product_list, solr.numFound()

def _django_search( query_dict ):
    form = ProductFilterForm(data = query_dict)
    
    if len(query_dict.keys()) > 1:
        if form.is_valid():
            data = form.cleaned_data
            for key, value in data.items():
                if not value:
                    del data[key]
            
            if 'id__in' in query_dict:
                data['id__in'] = query_dict['id__in'].split(',')
            
            if 'has_expired' in query_dict:
                data['expiry__lt'] = datetime.now()
            
            if 'is_valid' in query_dict:
                data['expiry__gte'] = datetime.now()
            
            Q_obj = Q()
            Q_obj.connector = data.pop("connector")
            Q_obj.children  = data.items()
            
            product_list = Product.objects.filter( Q_obj )
            num_found = product_list.count()
        else:
            error_msg(request, "Recherche non valide")
            product_list = Product.objects.none()
            num_found = 0
    else:
        product_list = Product.objects.none()
        num_found = 0
    
    return product_list, num_found


def _product_search( query_dict ):
    if 'q' in query_dict.keys():
        product_list, num_found = _solr_search( query_dict.dict() )
    elif len(query_dict.keys()) > 0:
        product_list, num_found = _django_search( query_dict )
    else:
        product_list = Product.objects.none()
        num_found = 0
    
    return product_list, num_found

@login_required
def index(request):
    query_dict = request.GET.copy()
    
    product_list, num_found = _product_search( query_dict )
    
    if request.user.has_perm("order.custom_view_local_provider") and not request.user.is_superuser:
        if not 'q' in query_dict.keys():
            product_list = Product.objects.filter( provider__is_local = True )
        else:
            product_list = product_list.filter( provider__is_local = True )
        num_found = product_list.count()
        product_count = Product.objects.filter( provider__is_local = True ).count()
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
@transaction.commit_on_success
def item(request, product_id):
    product = get_object_or_404(Product, id = product_id)
    if request.method == 'GET':
        form = ProductForm(instance = product, provider = product.provider)
        url_args = request.GET.urlencode()
    elif request.method == 'POST':
        data = request.POST.copy()
        url_args = data.pop('url_args')
        form = ProductForm(instance = product, data = data)
        if form.is_valid():
            if form.has_changed():
                orig_price = product.price
                product = form.save()
                if orig_price != product.price and product.has_expired():
                    product.expiry = datetime("31/12/%s" % datetime.now().year, "%d/%m/%Y")
                    product.save()
                    
                info_msg( request, u"Produit modifié avec succès." )
            return redirect( reverse('product_index') + '?' + url_args[0] )
    
    product_type = ContentType.objects.get_for_model(Product)
    return render(request, 'product/item.html',{
        'product': product,
        'product_type': product_type.id,
        'form': form,
        'url_args': url_args
    })


@login_required
@transaction.commit_on_success
def new(request):
    if request.method == 'GET':
        provider_id = request.GET.get('provider_id',None)
        if provider_id:
            provider = get_object_or_404( Provider, id = provider_id )
            form = ProductForm( provider = provider )
        elif request.user.has_perm("order.custom_view_local_provider"):
            provider = get_object_or_404( Provider, name = 'MAGASIN', is_local = True )
            form = ProductForm( provider = provider )
        else:
            provider = None
            form = ProductForm()
    elif request.method == 'POST':
        if 'provider' in request.POST and request.POST['provider']:
            provider = get_object_or_404( Provider, id = request.POST['provider'] )
            form = ProductForm( provider = provider, data = request.POST )
        else:
            provider = None
            form = ProductForm( data = request.POST )
        
        if form.is_valid():
            p = form.save()
            if p.provider.reseller:
                p.origin = p.provider.name
                p.provider = p.provider.reseller
                p.save()
            
            p.post_to_solr()
            
            info_msg( request, u"Produit ajouté avec succès." )
            return redirect( reverse('product_index') + "?reference=%s&connector=OR" % p.reference )
    
    return render(request, 'product/form.html', {
        'provider': provider,
        'form': form
    })


@login_required
@transaction.commit_on_success
def delete(request, product_id):
    product = get_object_or_404(Product, id = product_id)
    if request.method == 'GET':
        return render(request, "product/delete.html", {
            'product': product
        })
    elif request.method == 'POST':
        product.delete()
        info_msg( request, u"Produit supprimé avec succès." )
        return redirect( 'product_index' )


@login_required
def export_xls( request ):
    product_list, num_found = _product_search( request.GET.copy() )
    
    if request.user.has_perm("order.custom_view_local_provider"):
        if num_found == 0:
            product_list = Product.objects.all()
        product_list = product_list.filter( provider__is_local = True )
    
    wb = xlwt.Workbook()
    ws = wb.add_sheet("export")
    
    header = [u"FOURNISSEUR", u"DESIGNATION", u"REFERENCE", u"PRIX", u"CONDITIONNEMENT", 
    u"NOMENCLATURE", u"FOURNISSEUR D'ORIGINE", u"N°OFFRE", u"EXPIRATION", u"MISE A JOUR"]
    for col, title in enumerate(header): ws.write(0, col, title)
    
    row = 1
    
    for product in product_list:
        # if product.origin:
        #     if request.user.has_perm("order.custom_view_local_provider"):
        #         provider = u"%s" % product.origin
        #     else:
        #         provider = u"%s - %s" % (product.provider.name, product.origin)
        # else:
        #     provider = u"%s" % product.provider.name
        
        if product.expiry:
            expiry = product.expiry.strftime("%d/%m/%Y")
        else:
            expiry = u""
        
        ws.write( row, 0, product.provider.name )
        ws.write( row, 1, product.name )
        ws.write( row, 2, product.reference )
        ws.write( row, 3, product.price )
        ws.write( row, 4, product.packaging )
        ws.write( row, 5, product.nomenclature )
        ws.write( row, 6, product.origin )
        ws.write( row, 7, product.offer_nb )
        ws.write( row, 8, expiry )
        ws.write( row, 9, product.last_change.strftime("%d/%m/%Y") )
        row += 1
    
    response = HttpResponse(mimetype="application/ms-excel")
    response['Content-Disposition'] = 'attachment; filename=export_produit.xls'
    response['Content-Type'] = 'application/vnd.ms-excel; charset=utf-8'
    wb.save(response)

    return response

@login_required
@transaction.commit_on_success
def edit_list(request):
    if request.method == 'GET':
        product_list, num_found = _product_search( request.GET.copy() )
        
        if request.user.has_perm("order.custom_view_local_provider") and not request.user.is_superuser:
            product_list = product_list.filter( provider__is_local = True )
        
        return render(request, 'product/edit_list.html',{
            'filter_form': ProductFilterForm(),
            'edit_form': EditListForm(),
            'product_list': product_list,
            'url_args': request.GET.urlencode()
        })
    
    if request.method == 'POST':
        form = EditListForm( data = request.POST )
        
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
            
            product_list = Product.objects.filter( id__in = product_ids )
            
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
                info_msg( request, "Produits supprimés avec succès.")
                return redirect( reverse('product_edit_list') + "?" + request.POST["url_args"] )
            else:
                info_msg( request, "Liste de produits mise à jour avec succès." )
                return redirect( reverse('product_edit_list') + "?" + request.POST["url_args"] )
        else:
            url_args = dict( urlparse.parse_qsl( request.POST["url_args"] ) )
            product_list, filter_form = _product_search( url_args )
            
            return render(request, 'product/edit_list.html', {
                'edit_form': form,
                'product_list': product_list,
                'url_args': request.POST['url_args']
            })
    
