# coding: utf-8
from datetime import datetime, date
from decimal import Decimal

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

@login_required
def index(request):
	product_list = Product.objects.all()
	product_choices = ";".join( list(set([ unicode(p) for p in product_list ])) )
	
	form = ProductFilterForm(
		data = request.GET,
		product_choices = product_choices
	)
	if len(request.GET.keys()) > 1:
		if form.is_valid():
			data = form.cleaned_data
			for key, value in data.items():
				if not value:
					del data[key]
		
			if 'id__in' in request.GET:
				data['id__in'] = request.GET['id__in'].split(',')
		
			Q_obj = Q()
			Q_obj.connector = data.pop("connector")
			Q_obj.children  = data.items()
		
			product_list = product_list.filter( Q_obj )
		else:
			error_msg(request, "Recherche non valide")
	
	return direct_to_template(request, 'product/index.html',{
		'filter_form': form,
		'products': paginate( request, product_list, 50 ),
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
				p.provider = p.provider.reseller
				p.origin = p.provider.name
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
@transaction.commit_on_success
def edit_list(request):
	if request.method == 'GET':
		product_list = Product.objects.all()
		product_choices = ";".join( list(set([ unicode(p) for p in product_list ])) )
	
		form = ProductFilterForm(
			data = request.GET,
			product_choices = product_choices
		)
		if len(request.GET.keys()) > 0 and form.is_valid():
			data = form.cleaned_data
			for key, value in data.items():
				if not value:
					del data[key]
			
			if 'id__in' in request.GET:
				data['id__in'] = request.GET['id__in'].split(',')
			
			Q_obj = Q()
			Q_obj.connector = data.pop("connector")
			Q_obj.children  = data.items()
		
			product_list = product_list.filter( Q_obj )
		else:
			product_list = Product.objects.none()
		
		return direct_to_template(request, 'product/edit_list.html',{
			'filter_form': form,
			'edit_form': EditListForm(),
			'products': product_list,
			'url_args': urlencode(request.GET)
		})
	
	if request.method == 'POST':
		data = request.POST
		product_list = Product.objects.filter( id__in = data['product_ids'].split(',') )
		url_args = data['url_args']
		
		form = EditListForm( data = data )
		if form.is_valid():
			clean_data = form.cleaned_data
			percent_raise = clean_data.get('percent_raise', None)
			category = clean_data.get('category', None)
			sub_category = clean_data.get('sub_category', None)
			nomenclature = clean_data.get('nomenclature', None)
			offer_nb = clean_data.get('offer_nb',None)
			expiry = clean_data.get('expiry',None)
			delete_all = 'confirm_delete' in data
			
			for product in product_list:
				if delete_all:
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
			
			if delete_all:
				info_msg( request, "Produits supprimés avec succès.")
				return redirect('product_index')
			else:
				info_msg( request, "Liste de produits mise à jour avec succès." )
				return redirect( reverse('product_index') + '?connector=OR&id__in=' + data['product_ids'] )
		else:
			return direct_to_template(request, 'product/edit_list.html', {
				'edit_form': form,
				'products': product_list,
				'url_args': url_args
			})
	
