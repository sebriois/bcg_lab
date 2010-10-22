# coding: utf-8
from datetime import datetime, date

from django.shortcuts import get_object_or_404, redirect
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.views.generic.simple import direct_to_template

from order_manager.order.models import Cart

from order_manager.constants import *
from order_manager.utils import info_msg, error_msg, warn_msg

@login_required
def cart_index(request):
    if request.method == 'GET':
      cart, created = Cart.objects.get_or_create( user = request.user )
      
      cart_by_provider = {}
      for p in cart.products.all():
        if not p.provider.name in cart_by_provider:
          cart_by_provider[p.provider.name] = []
        cart_by_provider[p.provider.name].append(p)
      
      return direct_to_template(request, "order/cart.html", { 
        'cart': cart,
        'cart_by_provider': cart_by_provider
      })

@login_required
@transaction.commit_on_success
def cart_empty(request, cart_id):
    cart = get_object_or_404(Cart, id = cart_id)
    if request.method == 'GET':
      cart.products.clear()
      cart.save()
      return redirect('cart_index')
