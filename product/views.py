# coding: utf-8
from datetime import datetime, date
from decimal import Decimal
import urlparse

from django.shortcuts import get_object_or_404, redirect
from django.utils.http import urlencode
from django.core.urlresolvers import reverse
from django.db.models.query import Q
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.views.generic.simple import direct_to_template

from provider.models import Provider
from product.models import Product
from product.forms import ProductForm, ProductFilterForm, EditListForm
from order.models import Order, OrderItem
from attachments.models import Attachment

from constants import *
from utils import *

from haystack.query import SearchQuerySet

def _product_search( request_args ):
	# SEARCH WITH APACHE SOLR
	if "q" in request_args:
		results = SearchQuerySet().auto_query(request_args["q"])
		product_ids = []
		for r in results:
			if r and r.object and r.object.id: product_ids.append( r.object.id )
		product_list = Product.objects.filter( id__in = product_ids )
		form = ProductFilterForm()
		
	# ADVANCED SEARCH: with Django
	else:
		form = ProductFilterForm(data = request_args)
	
		if len(request_args.keys()) > 1:
			if form.is_valid():
				data = form.cleaned_data
				for key, value in data.items():
					if not value:
						del data[key]
			
				if 'id__in' in request_args:
					data['id__in'] = request_args['id__in'].split(',')
			
				Q_obj = Q()
				Q_obj.connector = data.pop("connector")
				Q_obj.children  = data.items()
			
				product_list = Product.objects.filter( Q_obj )
			else:
				error_msg(request, "Recherche non valide")
				product_list = Product.objects.none()
		else:
			product_list = Product.objects.none()
	
	return product_list, form

@login_required
def index(request):
	product_list, filter_form = _product_search( request.GET )
	
	if request.user.has_perm("order.custom_view_local_provider"):
		if len( request.GET.keys() ) == 0 or request.GET.keys() == ["page"]:
			product_list = Product.objects.filter( provider__is_local = True )
		else:
			product_list = product_list.filter( provider__is_local = True )
		product_count = Product.objects.filter( provider__is_local = True ).count()
	else:
		product_count = Product.objects.all().count()
	
	return direct_to_template(request, 'product/index.html',{
		'product_count': product_count,
		'search_count': product_list.count(),
		'filter_form': filter_form,
		'q_init': request.GET.get("q",""),
		'products': paginate( request, product_list, 25 ),
		'url_args': urlencode(request.GET)
	})

@login_required
@transaction.commit_on_success
def item(request, product_id):
	product = get_object_or_404(Product, id = product_id)
	if request.method == 'GET':
		form = ProductForm(instance = product, provider = product.provider)
		url_args = urlencode(request.GET)
	elif request.method == 'POST':
		data = request.POST.copy()
		url_args = data.pop('url_args')
		form = ProductForm(instance = product, data = data)
		if form.is_valid():
			if form.has_changed():
				form.save()
				info_msg( request, u"Produit modifié avec succès." )
			return redirect( reverse('product_index') + '?' + url_args[0] )
	
	product_type = ContentType.objects.get_for_model(Product)
	return direct_to_template(request, 'product/item.html',{
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
			provider = get_object_or_404( Provider, is_local = True )
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
			
			info_msg( request, u"Produit ajouté avec succès." )
			return redirect( reverse('product_index') + "?reference=%s&connector=OR" % p.reference )
	
	return direct_to_template(request, 'product/form.html', {
		'provider': provider,
		'form': form
	})

@login_required
@transaction.commit_on_success
def delete(request, product_id):
	product = get_object_or_404(Product, id = product_id)
	if request.method == 'GET':
		return direct_to_template(request, "product/delete.html", {
			'product': product
		})
	elif request.method == 'POST':
		product.delete()
		info_msg( request, u"Produit supprimé avec succès." )
		return redirect( 'product_index' )


@login_required
def export_xls( request ):
	product_list, filter_form = _product_search( request.GET )
	
	if request.user.has_perm("order.custom_view_local_provider"):
		product_list = product_list.filter( provider__is_local = True )
	
	wb = xlwt.Workbook()
	ws = wb.add_sheet("export")
	
	header = [u"FOURNISSEUR", u"DESIGNATION", u"CONDITIONNEMENT",u"REFERENCE", u"PRIX", 
	u"N°OFFRE", u"EXPIRATION", u"NOMENCLATURE", u"DERNIERE MISE A JOUR"]
	for col, title in enumerate(header): ws.write(0, col, title)
	
	row = 1
	
	for product in product_list:
		if product.origin:
			provider = u"%s - %s" % (product.provider.name, product.origin)
		else:
			provider = u"%s" % product.provider.name
		
		ws.write( row, 0, provider )
		ws.write( row, 1, product.name )
		ws.write( row, 2, product.packaging )
		ws.write( row, 3, product.reference )
		ws.write( row, 4, product.price )
		ws.write( row, 5, product.offer_nb )
		ws.write( row, 6, product.expiry.strftime("%d/%m/%Y") )
		ws.write( row, 7, product.nomenclature )
		ws.write( row, 8, product.last_change.strftime("%d/%m/%Y") )
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
		product_list, filter_form = _product_search( request.GET )
		
		if request.user.has_perm("order.custom_view_local_provider"):
			product_list = product_list.filter( provider__is_local = True )
		
		return direct_to_template(request, 'product/edit_list.html',{
			'filter_form': filter_form,
			'edit_form': EditListForm(),
			'product_list': product_list,
			'url_args': urlencode(request.GET)
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
			
			return direct_to_template(request, 'product/edit_list.html', {
				'edit_form': form,
				'product_list': product_list,
				'url_args': request.POST['url_args']
			})
	
