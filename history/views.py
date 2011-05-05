# encoding: utf-8
from datetime import datetime, date

from django.db.models.query import Q
from django.db import transaction
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, redirect
from django.template import Context, loader
from django.utils.http import urlencode
from django.views.generic.simple import direct_to_template

from provider.models import Provider
from product.models import Product
from order.models import Order, OrderItem
from order.forms import HistoryFilterForm

from constants import *
from utils import *

@login_required
def index(request):
  order_list = Order.objects.filter( date_delivered__isnull = False )
  
  if request.method == 'GET':
    form = HistoryFilterForm()
  
  elif request.method == 'POST':
    form = HistoryFilterForm( data = request.POST )
    
    if form.is_valid():
      data = form.cleaned_data
      
      for key, value in data.items():
        if not value:
          del data[key]
      
      Q_obj = Q()
      Q_obj.connector = data.pop("connector")
      Q_obj.children  = data.items()
      
      order_list = order_list.filter( Q_obj )
    else:
      error_msg( request, "Le formulaire n'a pas pu être validé.")
  else:
    error_msg( request, "This request method (%s) is not handled on this page" % request.method )
    return redirect( 'history' )
  
  order_list.order_by( 'date_delivered' )
  return direct_to_template( request, "order/history.html", {
    'filter_form': form,
    'orders': paginate( request, order_list )
  })
