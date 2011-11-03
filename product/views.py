# coding: utf-8
from datetime import datetime, date

from django.shortcuts import get_object_or_404, redirect
from django.utils.http import urlencode
from django.core.urlresolvers import reverse
from django.db.models.query import Q
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.views.generic.simple import direct_to_template

from provider.models import Provider
from product.models import Product
from product.forms import ProductForm, ProductFilterForm
from order.models import Order, OrderItem

from constants import *
from utils import *

@login_required
@team_required
@transaction.commit_on_success
def index(request):
	if request.method == 'GET':		return _product_list(request)
	if request.method == 'POST':	return _product_creation(request)

@login_required
@team_required
@transaction.commit_on_success
def item(request, product_id):
	product = get_object_or_404(Product, id = product_id)
	if request.method == 'GET':			return _product_detail(request, product)
	if request.method == 'PUT':			return _product_update(request, product)
	if request.method == 'DELETE':	return _product_delete(request, product)

@login_required
@team_required
def new(request):
	if "provider_id" in request.GET:
		provider = get_object_or_404( Provider, id = request.GET.get("provider_id", None) )
	else:
		provider = None
	
	form = ProductForm( provider = provider )
	return direct_to_template(request, 'product/form.html', {
		'provider': provider,
		'form': form
	})

@login_required
@team_required
def delete(request, product_id):
	product = get_object_or_404(Product, id = product_id)
	return direct_to_template(request, "product/delete.html", { 'product': product })

#--- Private views
def _product_list(request):
	product_list = Product.objects.all()
	
	product_choices = ";".join( [ unicode(p) for p in product_list ] )
	form = ProductFilterForm( data = request.GET, product_choices = product_choices )
	if len(request.GET.keys()) > 0 and form.is_valid():
		data = form.cleaned_data
		product_name = data['name']
		del data['name']
		
		for key, value in data.items():
			if not value:
				del data[key]
		
		Q_obj = Q()
		Q_obj.connector = data.pop("connector")
		Q_obj.children  = data.items()
		
		product_list = product_list.filter( Q_obj )
		
		if product_name:
			product_list = product_list.filter( name__icontains = product_name )
	
	return direct_to_template(request, 'product/index.html',{
		'filter_form': form,
		'products': paginate( request, product_list, 50 ),
		'url_params': urlencode(request.GET)
	})

def _product_detail(request, product):
	form = ProductForm(instance = product, provider = product.provider)
	return direct_to_template(request, 'product/item.html',{
		'product': product,
		'form': form
	})

def _product_creation(request):
	provider = get_object_or_404( Provider, id = request.POST.get('provider', None) )
	form = ProductForm( provider = provider, data = request.POST )
	
	if form.is_valid():
		form.save()
		info_msg( request, u"Produit ajouté avec succès." )
		return redirect( reverse('product_index') + "?provider=%s&connector=OR" % provider.name )
	else:
		return direct_to_template(request, 'product/form.html',{
			'provider': provider,
			'form': form
		})

def _product_update(request, product):
	form = ProductForm(instance = product, data = request.REQUEST)
	if form.is_valid():
		product = form.save()
		
		info_msg( request, u"Produit modifié avec succès." )
		return redirect( 'product_index' )
	else:
		return direct_to_template(request, 'product/item.html',{
			'product': product,
			'form': form
		})

def _product_delete(request, product):
	product.delete()
	info_msg( request, u"Produit supprimé avec succès." )
	return redirect( 'product_index' )
