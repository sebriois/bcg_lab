# coding: utf-8

from django.views.generic.simple import direct_to_template
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.template import Context, loader
from django.shortcuts import redirect
from django.conf import settings

from order.models import Order
from utils import *

@login_required
def home(request):
  # if is_secretary(request.user):
  #   return redirect('tab_orders')
  # 
  # if is_validator(request.user):
  #   return redirect('tab_validation')
  # 
  # return redirect('product_index')
  return direct_to_template( request, 'homepage.html', {})

def error(request):
  return direct_to_template( request, '500.html', {} )

@login_required
@POST_method
def send_message(request):
  subject = "[Commandes LBCMCP] " + request.POST.get('subject', 'Nouveau message')
  message = request.POST.get('message', None)
  emails = []
  for user_id in request.POST.get('to', None).split(','):
    user = User.objects.get(id = user_id)
    if user.email:
      emails.append(user.email)
    else:
      warn_msg(request, "Le message n'a pas pu être envoyé à %s, faute d'adresse email valide." % user)
  
  if not message:
    error_msg(request, "Veuillez saisir le texte du message.")
    return redirect('.')
  
  default_from = request.user.email and request.user.email or settings.DEFAULT_FROM_EMAIL
  
  template = loader.get_template('email_empty.txt')
  message = template.render( Context({ 'message': message }) )
  send_mail( subject, message, default_from, emails )
  info_msg(request, "Message envoyé avec succès.")
  return redirect(request.POST.get('next','home'))
