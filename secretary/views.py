# coding: utf-8
from datetime import date

from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.views.generic.simple import direct_to_template

from order.models import Order
from secretary.models import Budget, BudgetLine
from secretary.forms import BudgetForm, CreditBudgetForm, DebitBudgetForm

from utils import *

@login_required
@secretary_required
@transaction.commit_on_success
def index_budget(request):
  if request.method == "GET": return budgets(request)
  if request.method == "POST": return create_budget(request)

@login_required
@secretary_required
@transaction.commit_on_success
def index_budget_line(request):
  if request.method == "GET": return reports(request)
  if request.method == "POST": return create_budget_line(request)


@login_required
@secretary_required
@GET_method
def orders(request):
  order_list = Order.objects.filter( status__in = [2,3,4] )
  
  return direct_to_template(request, 'secretary/orders.html',{
      'orders': paginate( request, order_list ),
      'budget_lines': Budget.objects.filter( amount__gt = 0 ).order_by('team')
  })

@login_required
@secretary_required
@GET_method
def new_budget(request):
  return direct_to_template(request, 'secretary/form.html',{
    'form': BudgetForm()
  })

@login_required
@secretary_required
@transaction.commit_on_success
def credit_budget(request, budget_id):
  budget = get_object_or_404( Budget, id = budget_id )
  
  if request.method == "GET":
    return direct_to_template(request, "secretary/form_credit.html",{
      'budget': budget,
      'form': CreditBudgetForm( budget )
    })
  
  data = request.POST.copy()
  data.update({'name': budget.name})
  form = CreditBudgetForm( budget, data = data )
  if form.is_valid():
    budget_line = form.save( commit = False)
    budget.amount += budget_line.credit
    budget.save()
    budget_line.amount_left = budget.amount
    budget_line.save()
    
    info_msg(request, "Ligne de crédit ajoutée avec succès!")
    return redirect('secretary_reports')
  else:
    error_msg(request, "Le formulaire n'est pas valide.")
    return direct_to_template(request, 'secretary/form_credit.html',{
      'budget': budget,
      'form': form
    })

@login_required
@secretary_required
@transaction.commit_on_success
def debit_budget(request, budget_id):
  budget = get_object_or_404( Budget, id = budget_id )
  
  if request.method == "GET":
    return direct_to_template(request, "secretary/form_debit.html",{
      'budget': budget,
      'form': DebitBudgetForm( budget )
    })
  
  data = request.POST.copy()
  data.update({'name': budget.name})
  form = DebitBudgetForm( budget, data = data )
  if form.is_valid():
    budget_line = form.save( commit = False )
    budget_line.debit = budget_line.quantity * budget_line.product_price
    budget.amount -= budget_line.debit
    budget.save()
    budget_line.amount_left = budget.amount
    budget_line.save()
    info_msg(request, "Ligne de débit ajoutée avec succès!")
    return redirect('secretary_reports')
  else:
    error_msg(request, "Le formulaire n'est pas valide.")
    return direct_to_template(request, 'secretary/form_debit.html',{
      'budget': budget,
      'form': form
    })


@GET_method
def budgets(request):
  budget_list = Budget.objects.all()
  return direct_to_template(request, 'tab_budgets.html',{
    'budgets': paginate( request, budget_list )
  })

@login_required
@secretary_required
@POST_method
@transaction.commit_on_success
def create_budget(request):
  data = request.POST
  
  form = BudgetForm(data = data)
  if form.is_valid():
    budget = form.save()
    info_msg(request, "Ligne budgétaire ajoutée avec succès.")
    
    return redirect('secretary_budgets')
  else:
    error_msg(request, "Le formulaire n'est pas valide.")
    
    return direct_to_template(request, 'secretary/form.html',{
      'form': form
    })

@GET_method
def reports(request):
  budget_lines = BudgetLine.objects.filter( date__year = date.today().year )
  
  budget_name = request.GET.get("budget_name", None)
  if budget_name:
    budget_lines = budget_lines.filter( name = budget_name )
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
