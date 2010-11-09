# coding: utf-8
from datetime import datetime, date

from django.shortcuts import get_object_or_404, redirect
from django.db.models.query import Q
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.views.generic.simple import direct_to_template

from provider.models import Provider
from product.models import Product
from order.models import Order
from order.forms import OrderForm

from constants import *
from utils import info_msg, error_msg, warn_msg
from utils import superuser_required
from utils import paginate

@login_required
@transaction.commit_on_success
def index(request):
    if request.method == 'GET':   return _order_list(request)
    if request.method == 'POST':  return _order_creation(request)

@login_required
@transaction.commit_on_success
def item(request, order_id):
    order = get_object_or_404(Order, id = order_id)
    if request.method == 'GET':     return _order_detail(request, order)
    if request.method == 'PUT':     return _order_update(request, order)
    if request.method == 'DELETE':  return _order_delete(request, order)

@login_required
def new(request):
    return direct_to_template(request, 'order/creation_form.html', { 'form': ProductForm() })

@login_required
@superuser_required
def delete(request, order_id):
    """ Confirmation page for deletion. """
    order = get_object_or_404(Product, id = order_id)
    return direct_to_template(request, "order/delete.html", { 'order': order })

#--- Private views
def _order_list(request):
  order_list = Order.objects.filter()
  provider = request.GET.get('provider', None)
  
  if provider:
    order_list = order_list.filter( provider__id = provider )
  
  return direct_to_template(request, 'order/index.html',{
      'orders': paginate( request, order_list ),
      'providers': Provider.objects.all(),
      'provider': provider
  })

def _order_detail(request, order):
    form = ProductForm(instance = order)
    return direct_to_template(request, 'order/item.html',{
        'order': order,
        'form': form
    })

def _order_creation(request):
  form = ProductForm(request.POST)
  if form.is_valid():
    order = form.save()
    
    info_msg( request, u"Produit ajouté avec succès." )
    return redirect( 'order_index' )
  else:
    error_msg( request, u"Le formulaire n'a pas pu être validé." )
    return direct_to_template(request, 'order/creation_form.html',{
        'form': form
    })

def _order_update(request, order):
    form = ProductForm(instance = order, data = request.REQUEST)
    if form.is_valid():
        order = form.save()
        
        info_msg( request, u"Produit modifié avec succès." )
        return redirect( 'order_index' )
    else:
        error_msg( request, u"Le formulaire n'a pas pu être validé." )
        return direct_to_template(request, 'order/item.html',{
            'order': order,
            'form': form
        })

def _order_delete(request, order):
    order.delete()
    info_msg( request, u"Produit supprimé avec succès." )
    return redirect( 'order_index' )
