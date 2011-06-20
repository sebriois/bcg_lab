# encoding: utf-8
from datetime import datetime, date
from decimal import Decimal

from django.db.models.query import Q
from django.db import transaction
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.template import Context, loader
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, redirect
from django.utils.http import urlencode
from django.views.generic.simple import direct_to_template

from provider.models import Provider
from product.models import Product
from budget.models import Budget
from order.models import Order, OrderItem
from order.forms import OrderItemForm

from constants import *
from utils import *

@login_required
@GET_method
def tab_cart(request):
  """
  Panier
  """
  orders = Order.objects.filter(
    user = request.user,
    status = 0
  ).order_by('provider__name')
  
  return direct_to_template(request, "tab_cart.html", { 
    'order_list': orders,
    'next': 'tab_cart'
  })

@login_required
@GET_method
def tab_orders(request):
  """
  Commandes en cours
  """
  if is_secretary(request.user):
    order_list = Order.objects.filter( status__in = [2,3,4] )
  else:
    order_list = Order.objects.filter(
      team = get_team_member( request ).team,
      status__gt = 0,
      status__lt = STATE_CHOICES[-1][0]
    )
  
  return direct_to_template(request, 'tab_orders.html',{
      'orders': paginate( request, order_list ),
      'next': 'tab_orders'
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
    'budgets': Budget.objects.filter(team = team),
    'next': 'tab_validation'
  })



@login_required
@GET_method
def order_detail(request, order_id):
  order = get_object_or_404( Order, id = order_id )
  member = get_team_member( request )
  
  budgets = []
  if member.is_validator():
    for budget in Budget.objects.filter( team = member.team ):
      if budget.get_amount_left() > 0:
        budgets.append( budget )
  elif member.is_secretary() or member.is_admin():
    for budget in Budget.objects.all():
      if budget.get_amount_left() > 0:
        budgets.append( budget )
    
  return direct_to_template(request, 'order/item.html',{
    'order': order,
    'budgets': budgets
  })


@login_required
@transaction.commit_on_success
def orderitem_detail(request, orderitem_id):
  orderitem = get_object_or_404( OrderItem, id = orderitem_id )
  order = orderitem.order_set.get()
  
  if request.method == 'GET':
    form = OrderItemForm( instance = orderitem )
  elif request.method == 'POST':
    form = OrderItemForm( instance = orderitem, data = request.POST )
    if form.is_valid():
      form.save()
      
      # Send product changes by email to users in charge
      if orderitem.product_id and bool(request.POST.get('send_changes', 'False')):
        product = Product.objects.get(id = orderitem.product_id)
        template = loader.get_template('email_update_product.txt')
        subject = "[Commandes LBCMCP] Mise à jour d'un produit"
        emails = []
        for user in product.provider.users_in_charge.all():
          if user.email:
            emails.append(user.email)
          else:
            warn_msg(request, "Le message n'a pas pu être envoyé à %s, faute d'adresse email valide." % user)
          
        changed_data = []
        for attr in form.changed_data:
          lbl = orderitem._meta.get_field(attr).verbose_name
          val = getattr(orderitem, attr)
          changed_data.append( (lbl,val) )
        
        message = template.render( Context({ 
          'changed_data': changed_data,
          'product': product,
          'url': request.build_absolute_uri(product.get_absolute_url())
        }) )
        send_mail( subject, message, settings.DEFAULT_FROM_EMAIL, emails )
        
      info_msg(request, "Produit modifié avec succès.")
      return redirect(order)
    else:
      error_msg(request, "Le formulaire n'est pas valide.")
  
  return direct_to_template( request, 'order/orderitem_detail.html', {
    'form': form,
    'orderitem': orderitem,
    'order': order
  })


@login_required
@POST_method
@transaction.commit_on_success
def add_orderitem(request, order_id):
  order = get_object_or_404( Order, id = order_id )
  
  form = OrderItemForm( data = request.POST )
  if form.is_valid():
    item = form.save( commit = False )
    item.cost_type = request.POST['cost_type']
    item.save()
    order.items.add(item)
    info_msg( request, u"'%s' ajouté à la commande avec succès." % item.name )
  else:
    error_msg( request, "Le formulaire n'est pas valide, veuillez remplir les champs obligatoires." )
  
  return redirect(order)


@login_required
@GET_method
@transaction.commit_on_success
def del_orderitem(request, orderitem_id):
  item = get_object_or_404( OrderItem, id = orderitem_id )
  order = item.order_set.get()
  info_msg( request, u"'%s' supprimé avec succès." % item.name )
  item.delete()
  
  if order.items.all().count() == 0:
    warn_msg( request, "La commande ne contenant plus d'article, elle a également été supprimée.")
    order.delete()
  
  return redirect( request.GET.get('next', 'tab_orders') )


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
@secretary_required
@transaction.commit_on_success
def set_budget(request, order_id):
  order = get_object_or_404( Order, id = order_id )
  
  budget = request.GET.get("budget", None)
  if not budget or Budget.objects.filter( id = budget ).count() == 0:
    error_msg(request, "Veuillez sélectionner un budget valide.")
  else:
    order.budget = Budget.objects.get( id = budget )
    order.save()
  
  return redirect(order)


@login_required
@GET_method
@team_required
@transaction.commit_on_success
def set_next_status(request, order_id):
  order = get_object_or_404( Order, id = order_id )
  member = get_team_member(request)
  
  #              #
  #   STATUS 0:  #
  #              #
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
      message = template.render( Context({ 'order': order, 'url': reverse('tab_validation') }) )
      send_mail( subject, message, settings.DEFAULT_FROM_EMAIL, emails )
    else:
      warn_msg(request, "Aucun email de validation n'a pu être \
      envoyé puisqu'aucun validateur n'a renseigné d'adresse email.")
    
    if member.is_normal:
      return redirect( 'tab_cart' )
    
    if member.is_validator or member.is_admin:
      return redirect( 'tab_validation' )
  
  #              #
  #   STATUS 1   #
  #              #
  elif order.status == 1 and (member.is_validator or member.is_admin) and member.team == order.team:
    if order.provider.is_local:
      subject = "[Commandes LBCMCP] Nouvelle commande magasin"
      template = loader.get_template('email_local_provider.txt')
      message = template.render( Context({ 'order': order }) )
      send_mail( subject, message, settings.DEFAULT_FROM_EMAIL, [EMAIL_MAGASIN] )
      order.status = 5
      order.save()
      info_msg( request, "Un email a été envoyé au magasin pour la livraison de la commande." )
    else:
      budget_line = request.GET.get("budget", None)
      if not budget_line or Budget.objects.filter( id = budget_line, team = member.team ).count() == 0:
        error_msg(request, "Veuillez sélectionner une ligne budgétaire valide.")
      else:
        order.budget = Budget.objects.get( id = budget_line )
        order.status = 2
        order.save()
        info_msg( request, "Nouveau statut: '%s'." % order.get_status_display() )
    return redirect( 'tab_validation' )
  
  #              #
  #   STATUS 2   #
  #              #
  elif order.status == 2 and member.is_secretary:
    if order.budget.budget_type == 0: # ie. CNRS
      number = request.GET.get('number', None)
      if not number:
        error_msg(request, "Commande budget CNRS, veuillez saisir un numéro XLAB.")
        return redirect( 'tab_orders' )
      order.number = number
      order.status = 4 # Skip status 3 when CNRS budget
    else:
      order.status = 3
    order.save()
    
    info_msg( request, "Nouveau statut: '%s'." % order.get_status_display() )
  
  #              #
  #   STATUS 3   #
  #              #
  elif order.status == 3 and member.is_secretary:
    if order.budget.budget_type != 0: # ie. pas CNRS (UPS, etc.)
      number = request.GET.get('number', None)
      if not number:
        error_msg(request, "Veuillez saisir un numéro de commande.")
        return redirect( 'tab_orders' )
      order.number = number
    
    order.status = 4
    order.save()
    
    info_msg( request, "Nouveau statut: '%s'." % order.get_status_display() )
  
  #              #
  #   STATUS 4   #
  #              #
  elif order.status == 4:
    try:
      delivery_date = request.GET.get('delivery_date', None)
      delivery_date = datetime.strptime( delivery_date, "%d/%m/%Y" )
    except:
      error_msg(request, "Veuillez saisir une date valide (format jj/mm/aaaa).")
      return redirect( 'tab_orders' )
    
    order.date_delivered = delivery_date
    order.status = 5
    order.save()
    order.create_budget_line()
    order.save_to_history()
    # TODO: make a CRON job to weekly remove received orders
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
    user = request.user,
    date_delivered__isnull = True
  )
  orders.delete()
  
  info_msg( request, u"Panier vidé avec succès." )
  return redirect('tab_cart')


@login_required
@POST_method
@team_required
@transaction.commit_on_success
def cart_add(request):
  member = get_team_member( request )
  product = get_object_or_404( Product, id = request.POST.get('product_id') )
  quantity = request.POST.get('quantity')
  
  order, created = Order.objects.get_or_create(
    team      = member.team,
    user      = request.user,
    provider  = product.provider,
    status    = 0
  )
  order.add( product, quantity )
  
  url_arg = request.POST.get('url_params', '')
  url = reverse('product_index', current_app="product") + "?" + url_arg
  
  info_msg( request, u"Produit ajouté au panier avec succès." )
  return redirect( url )

@login_required
@POST_method
@team_required
@transaction.commit_on_success
def set_item_quantity(request):
  order_item = get_object_or_404( OrderItem, id = request.POST.get('orderitem_id') )
  order = order_item.order_set.get()
  quantity = int(request.POST.get('quantity'))
  
  if quantity == 0:
    order_item.delete()
    warn_msg( request, u"Produit retiré du panier.")
    if order.items.all().count() == 0:
      order.delete()
      warn_msg( request, u"Commande %s retirée du panier." % order.provider.name )
  elif quantity > 0:
    order_item.quantity = quantity
    order_item.save()
    info_msg( request, u"Quantité modifiée avec succès.")
  else:
    error_msg( request, u"Veuillez saisir une quantité positive." )
  
  return redirect(request.POST.get('next','tab_cart'))

