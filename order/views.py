# encoding: utf-8
from datetime import datetime, date
from decimal import Decimal

from django.db.models.query import Q
from django.db import transaction
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseServerError
from django.shortcuts import get_object_or_404, redirect
from django.template import Context, loader
from django.utils.http import urlencode
from django.views.generic.simple import direct_to_template

from provider.models import Provider
from product.models import Product
from budget.models import Budget, BudgetLine
from order.models import Order, OrderItem
from order.forms import OrderItemForm, AddDebitForm, AddCreditForm

from constants import *
from utils import *

@login_required
@GET_method
def tab_cart(request):
	orders = Order.objects.filter(
		team__in = get_teams(request.user),
		status = 0
	)
	if not request.user.has_perm('budget.custom_view_budget'):
		orders = orders.filter(
			Q(items__is_confidential = False) |
			Q(items__username = request.user.username)
		).distinct()
	
	return direct_to_template(request, "tab_cart.html", { 
		'order_list': orders.order_by('provider__name'),
		'credit_form': AddCreditForm(),
		'debit_form': AddDebitForm(),
		'next': 'tab_cart'
	})

@login_required
@GET_method
def tab_orders(request):
	if request.user.has_perm('order.custom_goto_status_4') and not request.user.is_superuser:
		order_list = Order.objects.filter(
			status__in = [2,3,4]
		).order_by('-status','last_change')
	elif request.user.has_perm("team.custom_view_teams") and not request.user.is_superuser:
		order_list = Order.objects.filter(status__in = [2,3,4])
	else:
		order_list = Order.objects.filter(
			team__in = get_teams( request.user ),
			status__in = [1,2,3,4]
		)
	
	# Exclude confidential orders
	if not request.user.has_perm('budget.custom_view_budget'):
		order_list = order_list.filter(
			Q(items__is_confidential = False) |
			Q(items__username = request.user.username)
		).distinct()
	
	return direct_to_template( request, "order/index.html", {
		'orders': paginate( request, order_list ),
		'next': 'tab_orders'
	})


@login_required
@GET_method
def tab_validation( request ):
	teams = get_teams( request.user )
	
	# ORDERS THAT CAN BE SEEN
	if request.user.has_perms(['team.custom_view_teams','order.custom_validate']):
		order_list = Order.objects.filter( status = 1 ).order_by('-date_created')
	elif request.user.has_perm('order.custom_validate'):
		order_list = Order.objects.filter( team__in = teams, status = 1 ).order_by('-date_created')
	else:
		not_allowed_msg( request )
		return redirect('home')
	
	# BUDGETS THAT CAN BE SELECTED
	if request.user.has_perms(['team.custom_view_teams','budget.custom_view_budget']):
		budget_list = Budget.objects.filter(is_active = True)
	elif request.user.has_perm('budget.custom_view_budget'):
		budget_list = Budget.objects.filter(team__in = teams, is_active = True)
	else:
		budget_list = Budget.objects.none()
	
	return direct_to_template( request, 'tab_validation.html', {
		'orders': paginate( request, order_list ),
		'budgets': budget_list,
		'credit_form': AddCreditForm(),
		'debit_form': AddDebitForm(),
		'next': 'tab_validation'
	})


@login_required
@GET_method
def order_detail(request, order_id):
	order = get_object_or_404( Order, id = order_id )
	
	if request.user.has_perms(['team.custom_view_teams','budget.custom_view_budget']):
		budget_list = Budget.objects.filter(is_active = True)
	elif request.user.has_perm('budget.custom_view_budget'):
		budget_list = Budget.objects.filter(team__in = get_teams(request.user), is_active = True)
	else:
		budget_list = Budget.objects.none()
	
	return direct_to_template(request, 'order/item.html', {
		'order': order,
		'budgets': budget_list,
		'credit_form': AddCreditForm(),
		'debit_form': AddDebitForm(),
		'next': order.get_absolute_url()
	})


@login_required
@transaction.commit_on_success
def orderitem_detail(request, orderitem_id):
	orderitem = get_object_or_404( OrderItem, id = orderitem_id )
	
	if request.method == 'GET':
		return _orderitem_get( request, orderitem )
	
	if request.method == 'POST':
		return _orderitem_update( request, orderitem )


def _orderitem_get(request, orderitem ):
	return direct_to_template( request, 'order/orderitem_detail.html', {
		'form': OrderItemForm( instance = orderitem ),
		'orderitem': orderitem,
		'order': orderitem.order_set.get()
	})

def _orderitem_update(request, orderitem):
	order = orderitem.order_set.get()
	
	data = request.POST.copy()
	data['provider'] = order.provider.name
	
	form = OrderItemForm( instance = orderitem, data = data )
	if form.is_valid():
		form.save()
		
		if order.number:
			orderitem.update_budget_line()
		
		if orderitem.product_id:
			orderitem.update_product()
		
		info_msg( request, "Commande modifiée avec succès.")
		return redirect(order)
	
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
	info_msg( request, request.POST.items())
	form = OrderItemForm( data = request.POST )
	if form.is_valid():
		item = form.save( commit = False )
		item.cost_type = request.POST['cost_type']
		item.save()
		order.items.add(item)
		
		if order.number:
			item.create_budget_line()
		
		info_msg( request, u"'%s' ajouté à la commande avec succès." % item.name )
	else:
		error_msg( request, "Le formulaire n'est pas valide, veuillez remplir les champs obligatoires. %s %s" % ( form.errors, request.POST.items() ) )
	
	return redirect( request.POST.get('next', order))

@login_required
@transaction.commit_on_success
def add_credit(request, order_id):
	order = get_object_or_404( Order, id = order_id )
	next = request.POST.get('next', 'tab_orders')
	form = AddCreditForm( data = request.POST )
	if form.is_valid():
		item = form.save( commit = False )
		item.username = request.POST['username']
		item.provider = order.provider.name
		item.save()
		order.items.add(item)
		
		if order.number:
			item.create_budget_line()
		
		info_msg( request, u"'%s' ajouté à la commande avec succès." % item.name )
	else:
		error_msg( request, u"Une erreur s'est produite lors de l'ajout de la remise. \
Merci de vérifier que tous les champs obligatoires ont bien été remplis.")
	return redirect( next )


@login_required
@POST_method
@transaction.commit_on_success
def add_debit(request, order_id):
	order = get_object_or_404( Order, id = order_id )
	next = request.POST.get('next', 'tab_orders')
	form = AddDebitForm( data = request.POST )
	if form.is_valid():
		item = form.save( commit = False )
		item.username = request.POST['username']
		item.provider = order.provider.name
		item.save()
		order.items.add(item)
		
		if order.number:
			item.create_budget_line()
		
		info_msg( request, u"'%s' ajouté à la commande avec succès." % item.name )
	else:
		error_msg( request, u"Une erreur s'est produite lors de l'ajout de frais. \
Merci de vérifier que tous les champs obligatoires ont bien été remplis.")
	
	return redirect( next )

@login_required
@GET_method
@transaction.commit_on_success
def del_orderitem(request, orderitem_id):
	item = get_object_or_404( OrderItem, id = orderitem_id )
	order = item.order_set.get()
	info_msg( request, u"'%s' supprimé avec succès." % item.name )
	
	if order.status == 0:
		next_page = request.GET.get('next', 'tab_cart')
	elif order.status == 1 and request.user.has_perm('order.custom_validate'):
		next_page = request.GET.get('next', 'tab_validation')
	elif order.status == 4:
		BudgetLine.objects.filter(orderitem_id = item.id).delete()
		next_page = 'tab_orders'
	else:
		next_page = request.GET.get('next', order)
	
	item.delete()
	
	if order.items.all().count() == 0:
		warn_msg( request, "La commande ne contenant plus d'article, elle a également été supprimée.")
		order.delete()
		next_page = 'tab_orders' 
	
	return redirect( next_page )

@login_required
@GET_method
@transaction.commit_on_success
def order_delete(request, order_id):
	order = get_object_or_404( Order, id = order_id )
	if order.status == 4:
		BudgetLine.objects.filter(order_id = order.id).delete()
	
	if order.status == 0:
		next_page = request.GET.get('next', 'tab_cart')
	elif order.status == 1 and request.user.has_perm('order.custom_validate'):
		next_page = request.GET.get('next', 'tab_validation')
	else:
		next_page = 'tab_orders'
	
	order.delete()
	
	info_msg( request, "Commande supprimée avec succès.")
	return redirect(next_page)


@login_required
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
	#		error_msg( request, "La date de livraison ne peut pas être inférieure à la date d'enregistrement de la commande.")
	#		return redirect( 'tab_orders' )
	
	order.set_as_delivered( delivery_date )
	info_msg( request, "Commande marquée comme livrée.")
	return redirect( 'tab_orders' )




					#################
					# AJAX REQUESTS #
					#################

@login_required
@GET_method
@transaction.commit_on_success
def set_notes(request, order_id):
	if not request.is_ajax():
		error_msg(request, 'Method %s not allowed at this URL' % request.method )
		return redirect( request.META.get('HTTP_REFERER', 'tab_orders') )
	
	order = get_object_or_404( Order, id = order_id )
	if 'notes' in request.GET:
		order.notes = request.GET['notes']
		order.save()
	
	return HttpResponse('ok')

@login_required
@GET_method
@transaction.commit_on_success
def set_number(request, order_id):
	if not request.is_ajax():
		error_msg(request, 'Method %s not allowed at this URL' % request.method )
		return redirect( request.META.get('HTTP_REFERER', 'tab_orders') )
	
	order = get_object_or_404( Order, id = order_id )
	
	if 'number' in request.GET:
		order.number = request.GET['number']
		
		if order.status == 3:
			order.status = 4
			order.save()
			order.create_budget_line()
		else:
			order.save()
			order.update_budget_lines()
		
		return HttpResponse(order.number)
	
	return HttpResponseServerError('order number is missing.')
	

@login_required
@GET_method
@transaction.commit_on_success
def set_budget(request, order_id):
	if not request.is_ajax():
		error_msg(request, 'Method %s not allowed at this URL' % request.method )
		return redirect( request.META.get('HTTP_REFERER', 'tab_orders') )
	
	budget_id = request.GET.get("budget_id", None)
	if not budget_id:
		return HttpResponseServerError('budget_id is missing.')
	
	order = get_object_or_404( Order, id = order_id )
	budget_id = int(budget_id)
	
	if budget_id > 0:
		budget = get_object_or_404( Budget, id = budget_id )
		order.budget = budget
	
	if budget_id == 0:
		# bugdet will be set by secretary
		order.budget = None
	
	order.save()
	return HttpResponse('ok')

@login_required
@GET_method
@transaction.commit_on_success
def set_item_quantity(request):
	if not request.is_ajax():
		error_msg(request, 'Method %s not allowed at this URL' % request.method )
		return redirect( request.META.get('HTTP_REFERER', 'tab_orders') )
	
	orderitem_id = request.GET.get('orderitem_id', None)
	quantity = request.GET.get('quantity', None)
	
	if not orderitem_id or not quantity:
		return HttpResponseServerError('orderitem_id and/or quantity are missing.')
	
	quantity = int(quantity)
	if quantity <= 0:
		return HttpResponseServerError( u"'%s': Veuillez saisir une quantité entière positive." % item.name )
	
	item = get_object_or_404( OrderItem, id = orderitem_id )
	item.quantity = quantity
	item.save()
	
	return HttpResponse('ok')


					################
					# ORDER STATUS #
					################

@login_required
@GET_method
@transaction.commit_on_success
def set_next_status(request, order_id):
	order = get_object_or_404( Order, id = order_id )
	
	if order.status == 0:
		return _move_to_status_1(request, order)
	
	elif order.status == 1 and request.user.has_perm('order.custom_validate'):
		if request.user.has_perm('team.custom_view_teams'):
			return _move_to_status_2(request, order)
		elif order.team.members.filter( user = request.user ):
			return _move_to_status_2(request, order)
		else:
			error_msg(request, "Vous ne disposez pas des permissions nécessaires pour valider cette commande")
			return redirect('tab_validation')
	
	elif order.status == 2 and request.user.has_perm('order.custom_goto_status_3'):
		return _move_to_status_3(request, order)
	
	elif order.status == 3 and request.user.has_perm('order.custom_goto_status_4'):
		return _move_to_status_4(request, order)
	
	elif order.status == 4:
		return _move_to_status_5(request, order)
	
	else:
		error_msg(request, "Vous n'avez pas les permissions nécessaires pour modifier le statut de cette commande")
	
	return redirect( 'tab_orders' )


def _move_to_status_1(request, order):
	order.status = 1
	order.save()
	info_msg( request, "Nouveau statut: '%s'." % order.get_status_display() )
	
	emails = []
	for member in order.team.members.all():
		user = member.user
		if user.has_perm('order.custom_validate') and not user.is_superuser and user.email and user.email not in emails:
			emails.append( user.email )
	
	if emails:
		subject = "[Commandes LBCMCP] Validation d'une commande (%s)" % order.get_full_name()
		template = loader.get_template('order/validation_email.txt')
		context = Context({ 'order': order, 'url': reverse('tab_validation') })
		message = template.render( context )
		send_mail( subject, message, settings.DEFAULT_FROM_EMAIL, emails )
	else:
		warn_msg(request, "Aucun email de validation n'a pu être \
		envoyé puisqu'aucun validateur n'a renseigné d'adresse email.")
	
	if request.user.has_perm('order.custom_validate'):
		return redirect( 'tab_validation' )
	
	return redirect( 'tab_cart' )

def _move_to_status_2(request, order):
	if order.provider.is_local:
		subject = "[Commandes LBCMCP] Nouvelle commande magasin"
		template = loader.get_template('email_local_provider.txt')
		message = template.render( Context({ 'order': order }) )
		send_mail( subject, message, settings.DEFAULT_FROM_EMAIL, [EMAIL_MAGASIN] )
		
		order.status = 5
		order.save()
		order.save_to_history()
		
		info_msg( request, "Un email a été envoyé au magasin pour la livraison de la commande." )
	else:
		budget_id = request.GET.get("budget", None)
		if budget_id:
			order.budget = Budget.objects.get( id = budget_id )
		
		order.status = 2
		order.save()
		info_msg( request, "Nouveau statut: '%s'." % order.get_status_display() )
	return redirect( request.GET.get('next','tab_validation') )

def _move_to_status_3(request, order):
	order.status = 3
	order.save()
	
	info_msg( request, "Nouveau statut: '%s'." % order.get_status_display() )
	return redirect('tab_orders')

def _move_to_status_4(request, order):
	number = request.GET.get('number', None)
	
	if not number:
		if order.budget.budget_type == 0: # ie. CNRS
			msg = "Commande CNRS, veuillez saisir le numéro de commande XLAB."
			
		else:
			msg = "Commande UPS, veuillez saisir le numéro de commande SIFAC."
		
		error_msg(request, msg)
		return redirect( 'tab_orders' )
	
	order.number = number
	order.status = 4
	order.save()
	order.create_budget_line()
	
	info_msg( request, "Nouveau statut: '%s'." % order.get_status_display() )
	return redirect('tab_orders')

def _move_to_status_5(request, order):
	try:
		delivery_date = request.GET.get('delivery_date', None)
		delivery_date = datetime.strptime( delivery_date, "%d/%m/%Y" )
		if delivery_date < order.date_created:
			error_msg(request, u"Veuillez saisir une date de livraison supérieure à la date de création de la commande.")
			return redirect(order)
	except:
		error_msg(request, u"Veuillez saisir une date valide (format jj/mm/aaaa).")
		return redirect( 'tab_orders' )
	
	order.date_delivered = delivery_date
	order.status = 5
	order.save()
	order.save_to_history()
	# TODO: make a CRON job to weekly remove received orders
	return redirect('tab_orders')


					################
					#	 CART VIEWS	 #
					################

@login_required
@POST_method
@transaction.commit_on_success
def cart_add(request):
	member = get_team_member( request )
	product = get_object_or_404( Product, id = request.POST.get('product_id') )
	quantity = request.POST.get('quantity')
	
	order, created = Order.objects.get_or_create(
		team		 = member.team,
		provider = product.provider,
		status	 = 0
	)
	item	= order.add( product, quantity )
	item.username = request.user.username
	item.save()
	
	url_arg = request.POST.get('url_params', '')
	url = reverse('product_index', current_app="product") + "?" + url_arg
	
	info_msg( request, u"Produit ajouté au panier avec succès." )
	return redirect( url )

