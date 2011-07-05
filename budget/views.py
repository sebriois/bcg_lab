# coding: utf-8
from datetime import date

from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, redirect
from django.views.generic.simple import direct_to_template

from order.models import Order
from budget.models import Budget, BudgetLine
from budget.forms import BudgetForm, CreditBudgetForm, DebitBudgetForm
from budget.forms import TransferForm

from utils import *

@login_required
@secretary_required
@transaction.commit_on_success
def index_budget(request):
	if request.method == "GET":		return _budget_list(request)
	if request.method == "POST":	return _budget_creation(request)
	return redirect('error')

@login_required
@secretary_required
@transaction.commit_on_success
def index_budgetline(request):
	if request.method == "GET":		return _budgetline_list(request)
	if request.method == "POST":	return _budgetline_creation(request)
	return redirect('error')

@login_required
@secretary_required
@transaction.commit_on_success
def item_budget(request, budget_id):
	budget = get_object_or_404( Budget, id = budget_id )
	if request.method == 'GET':		return _budget_detail( request, budget )
	if request.method == 'POST':	return _budget_update( request, budget )
	return redirect('error')

@login_required
@secretary_required
@GET_method
def new_budget(request):
	return direct_to_template(request, 'budget/form.html',{
		'form': BudgetForm()
	})


@login_required
@secretary_required
@transaction.commit_on_success
def credit_budget(request, budget_id):
	budget = get_object_or_404( Budget, id = budget_id )
	
	if request.method == "GET":
		return direct_to_template(request, "budget/form_credit.html",{
			'budget': budget,
			'form': CreditBudgetForm( budget )
		})
	
	if request.method == 'POST':
		data = request.POST.copy()
		data.update({'budget': budget.name})
		form = CreditBudgetForm( budget, data = data )
		
		if form.is_valid():
			bl = form.save( commit = False )
			bl.team					= budget.team.name
			bl.budget_id		= budget.id
			bl.nature				= budget.default_nature
			bl.budget_type	= budget.budget_type
			bl.credit_type	= budget.default_credit_type
			bl.quantity			= 1
			bl.credit				= bl.quantity * bl.product_price
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
@secretary_required
@transaction.commit_on_success
def debit_budget(request, budget_id):
	budget = get_object_or_404( Budget, id = budget_id )
	
	if request.method == "GET":
		return direct_to_template(request, "budget/form_debit.html",{
			'budget': budget,
			'form': DebitBudgetForm( budget )
		})
	
	data = request.POST.copy()
	data.update({'name': budget.name})
	form = DebitBudgetForm( budget, data = data )
	if form.is_valid():
		bl = form.save( commit = False )
		bl.team					= budget.team.name
		bl.budget_id		= budget.id
		bl.nature				= budget.default_nature
		bl.budget_type	= budget.budget_type
		bl.credit_type	= budget.default_credit_type
		bl.quantity			= 1
		bl.credit				= 0
		bl.debit				= bl.quantity * bl.product_price
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
def transfer_budget(request):
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
				product			= u"Virement vers budget %s" % budget2.name,
				team 				= budget1.team.name,
				budget_id 	= budget1.id,
				budget 			= budget1.name,
				nature 			= budget1.default_nature,
				budget_type	= budget1.budget_type,
				credit_type	= budget1.default_credit_type,
				quantity		= 1,
				debit				= amount,
				credit			= 0,
				product_price = amount
			)
			# CREDIT BUDGET2
			BudgetLine.objects.create(
				product			= u"Virement reçu du budget %s" % budget1.name,
				team 				= budget2.team.name,
				budget_id 	= budget2.id,
				budget 			= budget2.name,
				nature 			= budget2.default_nature,
				budget_type	= budget2.budget_type,
				credit_type	= budget2.default_credit_type,
				quantity		= 1,
				debit				= 0,
				credit			= amount,
				product_price = amount
			)
			return redirect('budgets')
			
	return direct_to_template(request, 'budget/transfer.html', {
		'form': form
	})


# 
#		PRIVATE VIEWS
# 

@GET_method
def _budget_list(request):
	budget_list = Budget.objects.all()
	return direct_to_template(request, 'tab_budgets.html',{
		'budgets': paginate( request, budget_list )
	})

@POST_method
def _budget_creation(request):
	form = BudgetForm(data = request.POST)
	
	if form.is_valid():
		budget = form.save()
		info_msg(request, "Ligne budgétaire ajoutée avec succès.")
		
		return redirect('budgets')
	else:
		return direct_to_template(request, 'budget/form.html',{
			'form': form
		})

@GET_method
def _budget_detail(request, budget):
	return direct_to_template( request, 'budget/item.html', {
		'budget': budget,
		'form': BudgetForm( instance = budget )
	})

@POST_method
def _budget_update(request, budget):
	form = BudgetForm(data = request.POST, instance = budget)
	
	if form.is_valid():
		form.save()
		info_msg(request, "Budget modifié avec succès.")
		
		return redirect('budgets')
	else:
		return direct_to_template(request, 'budget/item.html', {
			'budget': budget,
			'form': form
		})


@GET_method
def _budgetline_list(request):
	budget_lines = BudgetLine.objects.filter( date__year = date.today().year )
	
	budget_name = request.GET.get("budget_name", None)
	if budget_name:
		budget_lines = budget_lines.filter( budget = budget_name )
		try:
			budget = Budget.objects.get( name = budget_name )
		except:
			budget = None
	else:
		budget = None
	
	return direct_to_template(request, "tab_reports.html", {
		'budget': budget,
		'budget_lines' : paginate( request, budget_lines )
	})
