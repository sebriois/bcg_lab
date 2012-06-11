# coding: utf-8
from datetime import date
from decimal import Decimal
import xlwt

from django.utils.http import urlencode
from django.db import transaction
from django.db.models.query import Q
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, redirect
from django.views.generic.simple import direct_to_template

from order.models import Order
from budget.models import Budget, BudgetLine
from budget.forms import BudgetLineForm, BudgetLineFilterForm

from utils import *

@login_required
@GET_method
def index(request):
	if request.user.has_perms(['team.custom_view_teams','budget.custom_view_budget']):
		budget_lines = BudgetLine.objects.filter( is_active = True )
	elif request.user.has_perm('budget.custom_view_budget'):
		budget_lines = BudgetLine.objects.filter(
			is_active = True,
			team__in = [t.name for t in get_teams(request.user)]
		)
	else:
		not_allowed_msg(request)
		return redirect('home')
	
	# 
	# Filter budget_lines depending on received GET data
	form = BudgetLineFilterForm( user = request.user, data = request.GET )
	if len(request.GET.keys()) > 0 and form.is_valid():
		data = form.cleaned_data
		for key, value in data.items():
			if not value:
				del data[key]
		
		Q_obj = Q()
		Q_obj.connector = data.pop("connector")
		Q_obj.children	= data.items()
		
		budget_lines = budget_lines.filter( Q_obj )
	
	budgets = list(set(budget_lines.values_list('budget_id',flat=True)))
	if len(budgets) == 1:
		budget = Budget.objects.get( id = budgets[0], is_active = True )
	else:
		budget = Budget.objects.none()
	
	return direct_to_template(request, "budgetlines/index.html", {
		'budget': budget,
		'budget_lines' : budget_lines,
		'filter_form': form,
		'search_args': urlencode(request.GET)
	})

@login_required
@GET_method
def export_to_xls(request):
	# 
	# Filter budget_lines depending on received GET data
	form = BudgetLineFilterForm( user = request.user, data = request.GET )
	if len(request.GET.keys()) > 0 and form.is_valid():
		data = form.cleaned_data
		for key, value in data.items():
			if not value:
				del data[key]
		
		Q_obj = Q()
		Q_obj.connector = data.pop("connector")
		Q_obj.children	= data.items()
		
		budget_lines = BudgetLine.objects.filter( Q_obj )
	else:
		budget_lines = BudgetLine.objects.none()
	
	wb = xlwt.Workbook()
	ws = wb.add_sheet("export")
	
	header = [u"EQUIPE", u"BUDGET", u"N°CMDE",u"DATE", u"NATURE", 
	u"TUTELLE", u"FOURNISSEUR", u"COMMENTAIRE", u"DESIGNATION", 
	u"CREDIT", u"DEBIT", u"QUANTITE", u"TOTAL", u"MONTANT DISPO"]
	for col, title in enumerate(header): ws.write(0, col, title)
	
	prev_budget = None
	row = 1
	
	for bl in budget_lines.order_by("budget"):
		if prev_budget != bl.budget:
			if prev_budget: row += 1
			prev_budget = bl.budget
		
		ws.write( row, 0, bl.team )
		ws.write( row, 1, bl.budget )
		ws.write( row, 2, bl.number )
		ws.write( row, 3, bl.date.strftime("%d/%m/%Y") )
		ws.write( row, 4, bl.nature )
		ws.write( row, 5, bl.get_budget_type_display() )
		ws.write( row, 6, bl.provider )
		ws.write( row, 7, bl.offer )
		ws.write( row, 8, bl.product )
		ws.write( row, 9, bl.credit )
		ws.write( row, 10, bl.debit )
		ws.write( row, 11, bl.quantity )
		ws.write( row, 12, bl.product_price )
		ws.write( row, 13, str(bl.get_amount_left()) )
		row += 1
	
	response = HttpResponse(mimetype="application/ms-excel")
	response['Content-Disposition'] = 'attachment; filename=export_budget.xls'
	response['Content-Type'] = 'application/vnd.ms-excel; charset=utf-8'
	wb.save(response)
	
	return response

@login_required
@transaction.commit_on_success
def item(request, bl_id):
	bl = get_object_or_404( BudgetLine, id = bl_id )
	
	if request.method == 'GET':
		form = BudgetLineForm( instance = bl )
	
	elif request.method == 'POST':
		data = request.POST.copy()
		data['budget_id'] = int(data['budget'])
		form = BudgetLineForm( instance = bl, data = data )
		if form.is_valid():
			bl = form.save()
			bl.update_budget_relation()
			
			bl.is_active = True
			if data["cost_type"] == "credit":
				bl.credit = Decimal(data["cost"])
				bl.debit = 0
				bl.product_price = bl.credit * bl.quantity
			elif data["cost_type"] == "debit":
				bl.credit = 0
				bl.debit = Decimal(data["cost"])
				bl.product_price = bl.debit * bl.quantity
			bl.save()
			return redirect( reverse('budgetlines') + "?budget_id=%s&connector=OR" % data['budget_id'] )
	
	return direct_to_template( request, 'budgetlines/item.html', {
		'form': form,
		'bl': bl,
		'search_args': urlencode(request.GET)
	})


@login_required
@GET_method
def delete(request, bl_id):
	bl = get_object_or_404( BudgetLine, id = bl_id )
	budget_name = bl.budget
	bl.delete()
	return redirect( 'budgets' )

