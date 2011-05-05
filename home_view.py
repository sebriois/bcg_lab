# coding: utf-8

from django.views.generic.simple import direct_to_template
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.shortcuts import redirect

from order.models import Order
from utils import is_validator, is_secretary

@login_required
def home(request):
  if is_validator(request.user):
    return redirect('tab_validation')
  
  if is_secretary(request.user):
    return redirect('secretary_orders')
  
  return redirect('product_index')

def error(request):
  return direct_to_template( request, '500.html', {} )