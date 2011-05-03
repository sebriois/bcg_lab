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
from secretary.models import Budget
from order.models import Order, OrderItem
from order.forms import HistoryFilterForm

from constants import *
from utils import *

@login_required
@GET_method
def tab_cart(request):
  """
  Panier
  """
  orders = Order.objects.filter(
    username = request.user.username,
    status = 0
  )
  
  return direct_to_template(request, "tab_cart.html", { 
    'order_list': orders
  })

@login_required
@GET_method
def tab_orders(request):
  """
  Commandes en cours
  """
  if get_team_member( request ).is_secretary():
    return redirect("secretary_orders")
  
  order_list = Order.objects.filter(
    team = get_team_member( request ).team,
    status__gt = 0,
    status__lt = STATE_CHOICES[-1][0]
  )
  
  return direct_to_template(request, 'tab_orders.html',{
      'orders': paginate( request, order_list )
  })

@login_required
@validator_required
@GET_method
def tab_validation(request):
  """
  Commandes à valider
  """
  team = get_team_member( request ).team
  order_list = Order.objects.filter( team = team, status = 1 )
  
  return direct_to_template( request, 'tab_validation.html', {
    'orders': paginate( request, order_list ),
    'budget_lines': Budget.objects.filter(team = team)
  })




@login_required
@GET_method
def order_detail(request, order_id):
  if Order.objects.filter( id = order_id ).count() > 0:
    return direct_to_template(request, 'order/item.html',{
        'order': Order.objects.get( id = order_id )
    })
  else:
    return direct_to_template( request, 'order/404.html',{} )

@login_required
@GET_method
@transaction.commit_on_success
def order_delete(request, order_id):
  order = get_object_or_404( Order, id = order_id )
  order.delete()
  
  info_msg( request, "Commande supprimée avec succès.")
  return redirect('tab_orders')


@login_required
@team_required
@transaction.commit_on_success
def set_delivered(request, order_id):
  if not request.method == 'GET':
    error_msg( "This request method (%s) is not handled on this page" % request.method )
    return redirect( 'tab_orders' )
  
  order = get_object_or_404( Order, id = order_id )
  
  if "delivery_date" in request.GET:
    delivery_date_str = request.GET.get("delivery_date")
    try:
      delivery_date = datetime.strptime(delivery_date_str, "%d/%m/%Y")
    except:
      error_msg(request, "Merci de saisir une date au format jj/mm/aaaa. (Reçu: %s)" % delivery_date_str)
      return redirect( 'tab_orders' )
  else:
    delivery_date = datetime.now()
  
  # if order.date_created.date() > delivery_date.date():
  #   error_msg( request, "La date de livraison ne peut pas être inférieure à la date d'enregistrement de la commande.")
  #   return redirect( 'tab_orders' )
  
  order.set_as_delivered( delivery_date )
  info_msg( request, "Commande marquée comme livrée.")
  return redirect( 'tab_orders' )



@login_required
@GET_method
@team_required
@transaction.commit_on_success
def set_next_status(request, order_id):
  order = get_object_or_404( Order, id = order_id )
  member = get_team_member(request)
  
  if order.status == 0:
    order.status = 1
    order.save()
    info_msg( request, "Nouveau statut: '%s'." % order.get_status_display() )
    
    emails = []
    for member in order.team.members.filter( member_type = VALIDATOR ):
      if member.user.email and member.user.email not in emails:
        emails.append( member.user.email )
    
    if emails:
      subject = "[Commandes LBCMCP] Validation d'une commande (%s)" % order.get_full_name()
      template = loader.get_template('order/validation_email.txt')
      message = template.render( Context({ 'order': order }) )
      send_mail( subject, message, settings.DEFAULT_FROM_EMAIL, emails )
    else:
      warn_msg(request, "Aucun email de validation n'a pu être \
      envoyé puisqu'aucun validateur n'a renseigné d'adresse email.")
    
  elif order.status == 1 and (member.is_validator or member.is_admin) and member.team == order.team:
    budget_line = request.GET.get("budget_line", None)
    if not budget_line or Budget.objects.filter( id = budget_line, team = member.team ).count() == 0:
      error_msg(request, "Veuillez sélectionner une ligne budgétaire valide.")
    else:
      order.budget = Budget.objects.get( id = budget_line )
      order.status = 2
      order.save()
      info_msg( request, "Nouveau statut: '%s'." % order.get_status_display() )
  
  elif order.status == 2 and member.is_secretary:
    if order.budget.budget_type == 0: # ie. CNRS
      order_nb = request.GET.get('order_nb', None)
      if not order_nb:
        error_msg(request, "Veuillez saisir un numéro de commande.")
        return redirect( 'tab_orders' )
      order.order_nb = order_nb
      order.save()
      order.create_budget_line()
    
    order.status += 1
    order.save()
    info_msg( request, "Nouveau statut: '%s'." % order.get_status_display() )
    
  elif order.status == 3 and member.is_secretary:
    if order.budget.budget_type != 0: # ie. pas CNRS (UPS, etc.)
      order_nb = request.GET.get('order_nb', None)
      if not order_nb:
        error_msg(request, "Veuillez saisir un numéro de commande.")
        return redirect( 'tab_orders' )
      order.order_nb = order_nb
      order.save()
      order.create_budget_line()
    
    order.status += 1
    order.save()
    info_msg( request, "Nouveau statut: '%s'." % order.get_status_display() )
    
  elif order.status == 4:
    try:
      delivery_date = request.GET.get('delivery_date', None)
      delivery_date = datetime.strptime( delivery_date, "%d/%m/%Y" )
    except:
      error_msg(request, "Veuillez saisir une date valide (format jj/mm/aaaa).")
      return redirect( 'tab_orders' )
    
    order.date_delivered = delivery_date
    order.save()
  else:
    error_msg(request, "Vous n'avez pas les permissions nécessaires \
    pour modifier le statut de cette commande")
  
  return redirect( 'tab_orders' )


          ################
          #  CART VIEWS  #
          ################

@login_required
@GET_method
@transaction.commit_on_success
def cart_empty(request):
  orders = Order.objects.filter(
    status = 0,
    team = get_team_member(request).team,
    date_delivered__isnull = True
  )
  orders.delete()
  
  info_msg( request, u"Panier vidé avec succès." )
  return redirect('tab_cart')

@login_required
@GET_method
@team_required
@transaction.commit_on_success
def cart_add(request, product_id, quantity):
  product = get_object_or_404( Product, id = product_id )
  member = get_team_member( request )
  
  order, created = Order.objects.get_or_create(
    team      = member.team,
    username  = request.user.username,
    provider  = product.provider,
    status    = 0
  )
  
  item, created = order.items.get_or_create( product = product )
  item.quantity += int(quantity)
  item.save()
  
  order.update_price()
  
  info_msg( request, u"Produit ajouté au panier avec succès." )
  return redirect(
    reverse('product_index', current_app="product") + "?" + urlencode( request.GET )
  )

@login_required
@GET_method
@team_required
@transaction.commit_on_success
def set_item_quantity(request, item_id, quantity):
  order_item = get_object_or_404( OrderItem, id = item_id )
  order = order_item.order_set.get()
  quantity = int(quantity)
  
  if quantity == 0:
    order_item.delete()
    warn_msg( request, u"Produit retiré du panier.")
    if order.items.all().count() == 0:
      order.delete()
      warn_msg( request, u"Commande %s retirée du panier." % order.provider.name )
  elif quantity > 0:
    order_item.quantity = quantity
    order_item.save()
    order.update_price()
    info_msg( request, u"Panier modifié avec succès.")
  else:
    error_msg( request, u"Veuillez saisir une quantité positive." )
  
  return redirect('tab_cart')

