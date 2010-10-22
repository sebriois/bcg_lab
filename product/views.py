# coding: utf-8
from datetime import datetime, date

from django.shortcuts import get_object_or_404, redirect
from django.db.models.query import Q
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.views.generic.simple import direct_to_template

from order_manager.provider.models import Provider
from order_manager.product.models import Product
from order_manager.product.forms import ProductForm
from order_manager.order.models import Cart

from order_manager.constants import *
from order_manager.utils import info_msg, error_msg, warn_msg
from order_manager.utils import superuser_required
from order_manager.utils import paginate

@login_required
@superuser_required
@transaction.commit_on_success
def index(request):
    if request.method == 'GET':   return _product_list(request)
    if request.method == 'POST':  return _product_creation(request)

@login_required
@superuser_required
@transaction.commit_on_success
def item(request, product_id):
    product = get_object_or_404(Product, id = product_id)
    if request.method == 'GET':     return _product_detail(request, product)
    if request.method == 'PUT':     return _product_update(request, product)
    if request.method == 'DELETE':  return _product_delete(request, product)

@login_required
@superuser_required
def new(request):
    return direct_to_template(request, 'product/creation_form.html', { 'form': ProductForm() })

@login_required
@superuser_required
def delete(request, product_id):
    """ Confirmation page for deletion. """
    product = get_object_or_404(Product, id = product_id)
    return direct_to_template(request, "product/delete.html", { 'product': product })

@login_required
@transaction.commit_on_success
def add_to_cart(request, product_id):
  cart, create = Cart.objects.get_or_create( user = request.user )
  product = get_object_or_404(Product, id = product_id)
  cart.products.add( product )
  cart.save()
  return redirect('product_index')
  
#--- Private views
def _product_list(request):
  product_list = Product.objects.all()
  provider = request.GET.get('provider', None)
  
  if provider:
    product_list = product_list.filter( provider__id = provider )
  
  return direct_to_template(request, 'product/index.html',{
      # 'form': ProductFindForm(),
      'products': paginate( request, product_list ),
      'providers': Provider.objects.all(),
      'provider': provider
  })

def _product_detail(request, product):
    form = ProductForm(instance = product)
    return direct_to_template(request, 'product/item.html',{
        'product': product,
        'form': form
    })

def _product_creation(request):
  form = ProductForm(request.POST)
  if form.is_valid():
    product = form.save()
    
    info_msg( request, u"Produit ajouté avec succès." )
    return redirect( 'product_index' )
  else:
    error_msg( request, u"Le formulaire n'a pas pu être validé." )
    return direct_to_template(request, 'product/creation_form.html',{
        'form': form
    })

def _product_update(request, product):
    form = ProductForm(instance = product, data = request.REQUEST)
    if form.is_valid():
        product = form.save()
        
        info_msg( request, u"Produit modifié avec succès." )
        return redirect( 'product_index' )
    else:
        error_msg( request, u"Le formulaire n'a pas pu être validé." )
        return direct_to_template(request, 'product/item.html',{
            'product': product,
            'form': form
        })

def _product_delete(request, product):
    product.delete()
    info_msg( request, u"Produit supprimé avec succès." )
    return redirect( 'product_index' )
