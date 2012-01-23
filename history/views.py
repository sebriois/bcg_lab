# encoding: utf-8
from django.db.models.query import Q
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.views.generic.simple import direct_to_template

from history.models import History
from history.forms import HistoryFilterForm, BudgetHistoryFilterForm
from order.models import OrderItem
from budget.models import Budget, BudgetLine

from constants import *
from utils import *

@login_required
def history_orders(request):
	# Get initial history_list
	if request.user.has_perm('team.custom_view_teams'):
		history_list = History.objects.all()
	else:
		history_list = History.objects.filter(
			Q(items__username = request.user.username) |
			Q(team__in = [t.name for t in get_teams(request.user)])
		)
	
	# Filter history_list depending on received GET data
	form = HistoryFilterForm( user = request.user, data = request.GET )
	if len(request.GET.keys()) > 0 and form.is_valid():
		data = form.cleaned_data
		for key, value in data.items():
			if not value:
				del data[key]
		
		Q_obj = Q()
		Q_obj.connector = data.pop("connector")
		Q_obj.children	= data.items()
		
		history_list = history_list.filter( Q_obj )
	
	search_name = request.GET.get("items__name",None)
	search_ref = request.GET.get("items__reference",None)
	search_type = request.GET.get("items__category",None)
	search_subtype = request.GET.get("items__sub_category",None)
	
	if search_name or search_ref or search_type or search_subtype:
		display = "by_product"
		
		search_dict = {}
		if search_name:
			search_dict['name'] = search_name
		if search_ref:
			search_dict['reference'] = search_ref
		if search_type:
			search_dict['category'] = search_type
		if search_subtype:
			search_dict['sub_category'] = search_subtype
		
		Q_obj = Q()
		Q_obj.connector = request.GET['connector']
		Q_obj.children = search_dict.items()
		
		items_id = []
		for h in history_list:
			if request.GET['connector'] == 'OR':
				# FIXME: TIME CONSUMING
				for item in h.items.exclude( id__in = items_id ):
					items_id.append(item.id)
			elif request.GET['connector'] == 'AND':
				for item in h.items.filter( Q_obj ):
					if not item.id in items_id:
						items_id.append( item.id )
		
		objects = OrderItem.objects.filter( id__in = items_id ).distinct()
		objects = objects.order_by('-history__date_delivered')
		total = sum( [item.total_price() for item in objects] )
	else:
		display = "by_order"
		objects = history_list
		total = sum( [history.price for history in history_list.distinct()] )
	
	return direct_to_template( request, "history/orders.html", {
		'filter_form': form,
		'objects': paginate( request, objects.distinct() ),
		'display': display,
		'total': total
	})

@login_required
def item(request, item_id):
	item = get_object_or_404( History, id = item_id )
	
	return direct_to_template( request, 'history/item.html', {
		'history': item
	})

@login_required
def history_budgets(request):
	if request.user.has_perms(['team.custom_view_teams','budget.custom_view_budget']):
		budget_lines = BudgetLine.objects.filter( is_active = False )
	elif request.user.has_perm('budget.custom_view_budget'):
		budget_lines = BudgetLine.objects.filter(
			is_active = False,
			team__in = [t.name for t in get_teams(request.user)]
		)
	else:
		not_allowed_msg(request)
		return redirect('home')
	
	# 
	# Filter history_list depending on received GET data
	form = BudgetHistoryFilterForm( user = request.user, data = request.GET )
	if len(request.GET.keys()) > 0 and form.is_valid():
		data = form.cleaned_data
		for key, value in data.items():
			if not value:
				del data[key]
		
		Q_obj = Q()
		Q_obj.connector = data.pop("connector")
		Q_obj.children	= data.items()
		
		budget_lines = budget_lines.filter( Q_obj )
	
	return direct_to_template( request, 'history/budgets.html', {
		'filter_form': form,
		'objects': paginate( request, budget_lines.distinct() )
	})

