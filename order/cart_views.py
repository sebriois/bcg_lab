# coding: utf-8
from datetime import datetime, date

from django.shortcuts import get_object_or_404, redirect
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.views.generic.simple import direct_to_template

from order_manager.order.models import Cart
from order_manager.provider.models import Provider
from order_manager.product.models import Product

from order_manager.constants import *
from order_manager.utils import info_msg, error_msg, warn_msg

@login_required
def cart_index(request):
    if request.method == 'GET':
      cart, created = Cart.objects.get_or_create( user = request.user )
      
      cart_by_provider = {}
      for p in cart.products.all():
        if not p.provider in cart_by_provider:
          cart_by_provider[p.provider] = []
        cart_by_provider[p.provider].append(p)
      
      return direct_to_template(request, "order/cart.html", { 
        'cart': cart,
        'cart_by_provider': cart_by_provider
      })

@login_required
@transaction.commit_on_success
def cart_empty(request, cart_id):
    cart = get_object_or_404( Cart, id = cart_id )
    if request.method == 'GET':
      cart.products.clear()
      cart.save()
      info_msg( request, u"Panier vidé avec succès." )
    
    return redirect('cart_index')

@login_required
@transaction.commit_on_success
def cart_validate( request, cart_id, provider_id ):
    if request.method == 'GET':
      cart = get_object_or_404( Cart, id = cart_id )
      provider = get_object_or_404( Provider, id = provider_id )
      cart.turn_into_order( provider )
      info_msg( request, u"Commande %s passée avec succès." % provider.name )
    
    return redirect('cart_index')

@login_required
@transaction.commit_on_success
def cart_remove( request, cart_id, product_id ):
    if request.method == 'GET':
      cart = get_object_or_404( Cart, id = cart_id )
      product = get_object_or_404( Product, id = product_id )
      cart.products.remove( product )
      cart.save()
      info_msg( request, u"Produit retiré avec succès." )
    
    return redirect('cart_index')
