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
from budget.models import Budget
from order.models import Order, OrderItem
from order.forms import OrderItemForm, AddDebitForm, AddCreditForm

from constants import *
from utils import *

@login_required
@GET_method
def tab_cart(request):
	orders = Order.objects.filter( team__in = get_teams(request.user), status = 0 )
	
	return direct_to_template(request, "tab_cart.html", { 
		'order_list': orders.order_by('provider__name'),
		'next': 'tab_cart'
	})

@login_required
@GET_method
def tab_orders(request):
	if is_secretary(request.user) or is_super_secretary(request.user):
		order_list = Order.objects.filter( status__in = [2,3,4] )
		template = 'tab_orders_secretary.html'
	else:
		order_list = Order.objects.filter(
			team__in = get_teams( request.user ),
			status__in = [1,2,3,4]
		)
		template = 'tab_orders.html'
	
	return direct_to_template( request, template, {
		'orders': paginate( request, order_list ),
		'next': 'tab_orders'
	})


@login_required
@GET_method
def tab_validation(request):
	if is_admin(request.user) or is_super_validator(request.user):
		order_list = Order.objects.filter( status = 1 )
		budget_list = Budget.objects.all()
	elif is_validator(request.user):
		teams = get_teams( request.user )
		order_list = Order.objects.filter( team__in = teams, status = 1 )
		budget_list = Budget.objects.filter( team__in = teams )
	elif is_super_secretary(request.user):
		teams = get_teams( request.user )
		order_list = Order.objects.filter( team__in = teams, status = 1 )
		budget_list = Budget.objects.all()
	
	return direct_to_template( request, 'tab_validation.html', {
		'orders': paginate( request, order_list ),
		'budgets': budget_list,
		'next': 'tab_validation'
	})



@login_required
@GET_method
def order_detail(request, order_id):
	order = get_object_or_404( Order, id = order_id )
	budgets = []
	
	if is_secretary(request.user) or is_super_secretary(request.user) or is_admin(request.user):
		for budget in Budget.objects.all():
			if budget.get_amount_left() > 0:
				budgets.append( budget )
		template = 'order/order_details_secretary.html'
	
	elif is_validator(request.user):
		for budget in Budget.objects.filter( team__in = get_teams( request.user ) ):
			if budget.get_amount_left() > 0:
				budgets.append( budget )
		template = 'order/order_details_validator.html'
	
	else:
		template = 'order/order_details_normal.html'
	
	return direct_to_template(request, template, {
		'order': order,
		'budgets': budgets
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
			
			# Send product changes by email to users in charge
			# if orderitem.product_id and bool(request.POST.get('send_changes', 'False')):
			# 	product = Product.objects.get(id = orderitem.product_id)
			# 	template = loader.get_template('email_update_product.txt')
			# 	subject = "[Commandes LBCMCP] Mise à jour d'un produit"
			# 	emails = []
			# 	for user in product.provider.users_in_charge.all():
			# 		if user.email:
			# 			emails.append(user.email)
			# 		else:
			# 			warn_msg(request, "Le message n'a pas pu être envoyé à %s, \
			# 			faute d'adresse email valide." % user)
			# 
			# 	changed_data = []
			# 	for attr in form.changed_data:
			# 		lbl = orderitem._meta.get_field(attr).verbose_name
			# 		val = getattr(orderitem, attr)
			# 		changed_data.append( (lbl,val) )
			# 
			# 	message = template.render( Context({ 
			# 		'changed_data': changed_data,
			# 		'product': product,
			# 		'url': request.build_absolute_uri(product.get_absolute_url())
			# 	}) )
			# 	send_mail( subject, message, settings.DEFAULT_FROM_EMAIL, emails )
		
		info_msg( request, "Commande modifiée avec succès.")
		return redirect( order )
	
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
	
	if request.method == 'GET':
		next = request.GET.get('next', 'tab_orders')
		form = AddCreditForm()
	elif request.method == 'POST':
		next = request.POST.get('next', 'tab_orders')
		form = AddCreditForm( data = request.POST )
		if form.is_valid():
			item = form.save( commit = False )
			item.username = request.POST['username']
			item.save()
			order.items.add(item)
			
			if order.number:
				item.create_budget_line()
			
			info_msg( request, u"'%s' ajouté à la commande avec succès." % item.name )
			return redirect( next )
	
	return direct_to_template( request, "order/add_credit.html", {
		'order': order,
		'form': form,
		'next': next
	})

@login_required
@transaction.commit_on_success
def add_debit(request, order_id):
	order = get_object_or_404( Order, id = order_id )
	
	if request.method == 'GET':
		next = request.GET.get('next', 'tab_orders')
		form = AddDebitForm()
	elif request.method == 'POST':
		next = request.POST.get('next', 'tab_orders')
		form = AddDebitForm( data = request.POST )
		if form.is_valid():
			item = form.save( commit = False )
			item.username = request.POST['username']
			item.save()
			order.items.add(item)
			
			if order.number:
				item.create_budget_line()
			
			info_msg( request, u"'%s' ajouté à la commande avec succès." % item.name )
			return redirect( next )
	
	return direct_to_template( request, "order/add_debit.html", {
		'order': order,
		'form': form,
		'next': next
	})

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
		return redirect('tab_orders')
	
	return redirect( order )

@login_required
@GET_method
@transaction.commit_on_success
def order_delete(request, order_id):
	order = get_object_or_404( Order, id = order_id )
	order.delete()
	
	info_msg( request, "Commande supprimée avec succès.")
	return redirect('tab_orders')


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
@transaction.commit_on_success
def set_notes(request, order_id):
	if not request.is_ajax():
		error_msg(request, 'Method %s not allowed at this URL' % request.method )
		return redirect( request.META.get('HTTP_REFERER', 'tab_orders') )
	
	order = get_object_or_404( Order, id = order_id )
	if 'notes' in request.GET:
		order.notes = requsest.GET['notes']
		order.save()
	
	return HttpResponse('ok')

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
	
	elif order.status == 1:
		user_can_validate = order.team.members.filter( 
			user = request.user,
			member_type = VALIDATOR
		).count() > 0
		if user_can_validate or is_super_validator(request.user):
			return _move_to_status_2(request, order)
		else:
			error_msg(request, "Vous n'avez pas les permissions nécessaires \
			pour valider une commande")
			return redirect('tab_validation')
	
	elif order.status == 2 and ( is_secretary(request.user) or is_super_secretary(request.user) ):
		return _move_to_status_3(request, order)
	
	elif order.status == 3 and ( is_secretary(request.user) or is_super_secretary(request.user) ):
		return _move_to_status_4(request, order)
	
	elif order.status == 4:
		return _move_to_status_5(request, order)
	
	else:
		error_msg(request, "Vous n'avez pas les permissions nécessaires \
		pour modifier le statut de cette commande")
	
	return redirect( 'tab_orders' )


def _move_to_status_1(request, order):
	order.status = 1
	order.save()
	info_msg( request, "Nouveau statut: '%s'." % order.get_status_display() )
	
	emails = []
	for member in order.team.members.filter( member_type__in = [VALIDATOR, SUPER_SECRETARY] ):
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
	
	if is_validator(request.user):
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
	return redirect( 'tab_validation' )

def _move_to_status_3(request, order):
	if order.budget.budget_type == 0: # ie. CNRS
		number = request.GET.get('number', None)
		if not number:
			error_msg(request, "Commande CNRS, veuillez saisir le numéro de commande XLAB.")
			return redirect( 'tab_orders' )
		
		order.number = number
		order.status = 4 # Skip status 3 when CNRS budget
		order.save()
		order.create_budget_line()
	else:
		order.status = 3
		order.save()
	
	info_msg( request, "Nouveau statut: '%s'." % order.get_status_display() )
	return redirect('tab_orders')

def _move_to_status_4(request, order):
	if order.budget.budget_type != 0: # ie. pas CNRS (UPS, etc.)
		number = request.GET.get('number', None)
		if not number:
			error_msg(request, "Commande UPS, veuillez saisir le numéro de commande SIFAC.")
			return redirect( 'tab_orders' )
		
		order.number = number
		order.status = 4
		order.save()
		order.create_budget_line()
	
	else:
		order.status = 4
		order.save()
	
	info_msg( request, "Nouveau statut: '%s'." % order.get_status_display() )
	return redirect('tab_orders')

def _move_to_status_5(request, order):
	try:
		delivery_date = request.GET.get('delivery_date', None)
		delivery_date = datetime.strptime( delivery_date, "%d/%m/%Y" )
	except:
		error_msg(request, "Veuillez saisir une date valide (format jj/mm/aaaa).")
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

