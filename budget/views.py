# coding: utf-8
from datetime import date
from decimal import Decimal
import urllib

from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, redirect
from django.views.generic.simple import direct_to_template

from budget.models import Budget, BudgetLine
from budget.forms import BudgetForm, CreditBudgetForm, DebitBudgetForm
from budget.forms import TransferForm

from utils import *

@login_required
def index(request):
	if request.user.has_perms(['team.custom_view_teams','budget.custom_view_budget']):
		budget_list = Budget.objects.filter( is_active = True )
	elif request.user.has_perm("budget.custom_view_budget"):
		budget_list = Budget.objects.filter(
			is_active = True,
			team__in = get_teams(request.user)
		)
	else:
		not_allowed_msg(request)
		return redirect('home')

	return direct_to_template(request, 'budget/index.html',{
		'budgets': paginate( request, budget_list )
	})

@login_required
@transaction.commit_on_success
def item(request, budget_id):
	budget = get_object_or_404( Budget, id = budget_id )
	
	if request.method == 'GET':
		form = BudgetForm( instance = budget )
	elif request.method == 'POST':
		form = BudgetForm(data = request.POST, instance = budget)
		if form.is_valid():
			form.save()
			info_msg(request, "Budget modifié avec succès.")
			return redirect('budgets')
	else:
		return redirect('error')
		
	return direct_to_template(request, 'budget/item.html', {
		'budget': budget,
		'form': form
	})


@login_required
@transaction.commit_on_success
def new(request):
	if request.method == 'GET':
		form = BudgetForm()
	elif request.method == 'POST':
		form = BudgetForm(data = request.POST)
		if form.is_valid():
			data = form.cleaned_data
			for nature in ['fo','mi','sa','eq']:
				if data[nature]:
					budget = Budget.objects.create(
						team = data['team'],
						name = data['name'] + '-' + nature.upper(),
						default_origin = data.get('origin',None),
						budget_type = data['budget_type'],
						default_nature = nature.upper(),
						tva_code = data.get('tva_code',None),
						domain = data.get('domain',None)
					)
					budget.credit(data[nature])
			
			info_msg(request, "Budget ajouté avec succès.")
			return redirect('budgets')
	else:
		return redirect('error')
		
	return direct_to_template(request, 'budget/form.html',{
		'form': form
	})


@login_required
@transaction.commit_on_success
def credit(request, budget_id):
	budget = get_object_or_404( Budget, id = budget_id )
	
	if request.method == "GET":
		return direct_to_template(request, "budget/form_credit.html",{
			'budget': budget,
			'form': CreditBudgetForm( budget ),
			'prev': request.META.get('HTTP_REFERER','') + urllib.urlencode(request.GET)
		})
	
	data = request.POST.copy()
	data.update({ 'budget': budget.name }) # otherwise, form is not valid
	
	form = CreditBudgetForm( budget, data = data )
	
	if form.is_valid():
		bl = form.save( commit = False )
		bl.team					= budget.team.name
		bl.budget_id		= budget.id
		bl.nature				= budget.default_nature
		bl.budget_type	= budget.budget_type
		bl.origin				= budget.default_origin
		bl.quantity			= 1
		bl.credit				= bl.product_price
		bl.debit				= 0
		bl.save()
		
		info_msg(request, "Ligne de crédit ajoutée avec succès!")
		return redirect( reverse('budgetlines') + "?budget_name=%s" % budget.name )
	else:
		return direct_to_template(request, 'budget/form_credit.html',{
			'budget': budget,
			'form': form
		})


@login_required
@transaction.commit_on_success
def debit(request, budget_id):
	budget = get_object_or_404( Budget, id = budget_id )
	
	if request.method == "GET":
		return direct_to_template(request, "budget/form_debit.html",{
			'budget': budget,
			'form': DebitBudgetForm( budget ),
			'prev': request.META.get('HTTP_REFERER','') + urllib.urlencode(request.GET)
		})
	
	data = request.POST.copy()
	data.update({ 'budget': budget.name }) # otherwise, form is not valid
	
	form = DebitBudgetForm( budget, data = data )
	if form.is_valid():
		bl = form.save( commit = False )
		bl.team					= budget.team.name
		bl.budget_id		= budget.id
		bl.nature				= budget.default_nature
		bl.budget_type	= budget.budget_type
		bl.origin				= budget.default_origin
		bl.quantity			= 1
		bl.credit				= 0
		bl.debit				= bl.product_price
		bl.save()
		
		info_msg(request, "Ligne de débit ajoutée avec succès!")
		return redirect( reverse('budgetlines') + "?budget_name=%s" % budget.name )
	else:
		return direct_to_template(request, 'budget/form_debit.html',{
			'budget': budget,
			'form': form
		})


@login_required
@transaction.commit_on_success
def transfer(request):
	if request.method == 'GET':
		form = TransferForm()
	elif request.method == 'POST':
		form = TransferForm( data = request.POST )
		if form.is_valid():
			data = form.cleaned_data
			budget1 = data['budget1']
			budget2 = data['budget2']
			amount	= data['amount']
			
			# DEBIT BUDGET1
			BudgetLine.objects.create(
				product			= u"Virement vers %s" % budget2.name,
				team 				= budget1.team.name,
				budget_id 	= budget1.id,
				budget 			= budget1.name,
				nature 			= budget1.default_nature,
				budget_type	= budget1.budget_type,
				origin	= budget1.default_origin,
				quantity		= 1,
				debit				= amount,
				credit			= 0,
				product_price = amount
			)
			# CREDIT BUDGET2
			BudgetLine.objects.create(
				product			= u"Virement reçu de %s" % budget1.name,
				team 				= budget2.team.name,
				budget_id 	= budget2.id,
				budget 			= budget2.name,
				nature 			= budget2.default_nature,
				budget_type	= budget2.budget_type,
				origin	= budget2.default_origin,
				quantity		= 1,
				debit				= 0,
				credit			= amount,
				product_price = amount
			)
			return redirect('budgets')
			
	return direct_to_template(request, 'budget/transfer.html', {
		'form': form
	})


@login_required
@transaction.commit_on_success
def toggle(request, budget_id):
	budget = get_object_or_404( Budget, id = budget_id )
	budget.is_active = not budget.is_active
	budget.save()
	
	for bl in BudgetLine.objects.filter( budget_id = budget.id ):
		bl.is_active = budget.is_active
		bl.save()
	
	return redirect('budgets')

