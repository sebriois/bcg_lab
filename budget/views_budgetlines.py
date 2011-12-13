# coding: utf-8
from datetime import date
from decimal import Decimal
import urllib

from django.db import transaction
from django.db.models.query import Q
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
	# Filter history_list depending on received GET data
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
		'search_args': urllib.urlencode(request.GET)
	})



@login_required
@transaction.commit_on_success
def item(request, bl_id):
	bl = get_object_or_404( BudgetLine, id = bl_id )
	
	if request.method == 'GET':
		form = BudgetLineForm( instance = bl )
	
	elif request.method == 'POST':
		data = request.POST
		form = BudgetLineForm( instance = bl, data = data )
		if form.is_valid():
			bl = form.save( commit = False )
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
			return redirect( reverse('budgetlines') + "?budget_name=%s" % bl.budget )
	
	return direct_to_template( request, 'budgetlines/item.html', {
		'form': form,
		'bl': bl,
		'search_args': urllib.urlencode(request.GET)
	})


@login_required
@GET_method
def delete(request, bl_id):
	bl = get_object_or_404( BudgetLine, id = bl_id )
	budget_name = bl.budget
	bl.delete()
	return redirect( reverse('budgetlines') + "?budget_name=%s" % budget_name )

@login_required
def history(request):
	return direct_to_template( request, 'history/budgets.html')


	# @GET_method
	# def budgetline_export(request):
	# 	wb = xlwt.Workbook()
	# 	green = xlwt.easyxf(
	# 		"""
	# 		pattern:
	# 			fore_color: green
	# 		"""
	# 	)
	# 	red = xlwt.easyxf(
	# 		"""
	# 		pattern:
	# 			fore_color: red
	# 		"""
	# 	)
	# 	budgets = request.GET['budget_names'].split(';')
	# 	for budget_name in budgets:
	# 		ws = wb.add_sheet(budget_name)
	# 
	# 		ws.write(0,0,'BUDGET')
	# 		ws.write(0,1,'N°CMDE')
	# 		ws.write(0,2,'DATE')
	# 		ws.write(0,3,'NATURE')
	# 		ws.write(0,4,'TUTELLE')
	# 		ws.write(0,5,'ORIGINE')
	# 		ws.write(0,6,'FOURNISSEUR')
	# 		ws.write(0,7,'OFFRE')
	# 		ws.write(0,8,'DESIGNATION')
	# 		ws.write(0,9,'REFERENCE')
	# 		ws.write(0,10,'CREDIT')
	# 		ws.write(0,11,'DEBIT')
	# 		ws.write(0,12,'QUANTITE')
	# 		ws.write(0,13,'TOTAL')
	# 		ws.write(0,14,'MONTANT DISPO')
	# 
	# 		row = 1
	# 		for bl in budget_lines.filter( budget = budget_name ):
	# 			ws.write( row, 0, budget_name )
	# 			ws.write( row, 1, bl.number )
	# 			ws.write( row, 2, bl.date )
	# 			ws.write( row, 3, bl.nature )
	# 			ws.write( row, 4, bl.get_budget_type_display() )
	# 			ws.write( row, 5, bl.origin )
	# 			ws.write( row, 6, bl.provider )
	# 			ws.write( row, 7, bl.offer )
	# 			ws.write( row, 8, bl.product )
	# 			ws.write( row, 9, bl.ref )
	# 			ws.write( row, 10, bl.credit )
	# 			ws.write( row, 11, bl.debit )
	# 			ws.write( row, 12, bl.quantity )
	# 			ws.write( row, 13, bl.product_price )
	# 			ws.write( row, 14, bl.get_amount_left )
	# 			row += 1
	# 	
	# 	response = HttpResponse(mimetype="application/ms-excel")
	# 	response['Content-Disposition'] = 'attachment; filename=export.xls'
	# 	wb.save(response)
	# 	
	# 	return response
