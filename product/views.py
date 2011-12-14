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
def index(request):
	product_list = Product.objects.all()
	product_choices = ";".join( [ unicode(p) for p in product_list ] )
	
	form = ProductFilterForm( data = request.GET, product_choices = product_choices )
	if len(request.GET.keys()) > 0 and form.is_valid():
		data = form.cleaned_data
		for key, value in data.items():
			if not value:
				del data[key]
		
		Q_obj = Q()
		Q_obj.connector = data.pop("connector")
		Q_obj.children  = data.items()
		
		product_list = product_list.filter( Q_obj )
	
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
		url_args = request.GET.get('url_args',None)
	elif request.method == 'POST':
		data = request.POST.copy()
		url_args = data.pop('url_args')
		form = ProductForm(instance = product, data = data)
		if form.is_valid():
			form.save()
			info_msg( request, u"Produit modifié avec succès." )
			return redirect( reverse('product_index') + url_args )
	
	return direct_to_template(request, 'product/item.html',{
		'product': product,
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
			form = ProductForm()
	elif request.method == 'POST':
		if 'provider' in request.POST and request.POST['provider']:
			provider = get_object_or_404( Provider, id = request.POST['provider'] )
			form = ProductForm( provider = provider, data = request.POST )
		else:
			form = ProductForm( data = request.POST )
		
		if form.is_valid():
			p = form.save()
			info_msg( request, u"Produit ajouté avec succès." )
			return redirect( reverse('product_index') + "?name=%s&connector=OR" % p.name )
	
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
