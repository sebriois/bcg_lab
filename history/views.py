# encoding: utf-8
from django.db.models.query import Q
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.views.generic.simple import direct_to_template

from history.models import History
from history.forms import HistoryFilterForm

from constants import *
from utils import *

@login_required
def index(request):
	# Get initial history_list
	if is_secretary(request.user) or is_super_secretary(request.user) or is_super_validator(request.user): # admin is also a 'secretary'
		history_list = History.objects.all()
	else:
		team_names = []
		for team in get_teams(request.user):
			if not team.name in team_names:
				team_names.append(team.name)
		history_list = History.objects.filter( team__in = team_names )
	
	# Filter history_list depending on received GET data
	form = HistoryFilterForm( user = request.user, data = request.GET )
	if len(request.GET.keys()) > 0 and form.is_valid():
		data = form.cleaned_data
		product_name = data['items__name']
		del data['items__name']
		
		for key, value in data.items():
			if not value:
				del data[key]
		
		Q_obj = Q()
		Q_obj.connector = data.pop("connector")
		Q_obj.children	= data.items()
		
		history_list = history_list.filter( Q_obj )
		
		if product_name:
			history_list = history_list.filter( items__name__icontains = product_name )
	
	if "items__name" in request.GET.keys() or "items__reference" in request.GET.keys():
		display = "by_product"
	else:
		display = "by_order"
	
	return direct_to_template( request, "history/orders.html", {
		'filter_form': form,
		'history': paginate( request, history_list ),
		'display': display
	})

@login_required
def item(request, item_id):
	item = get_object_or_404( History, id = item_id )
	
	return direct_to_template( request, 'history/item.html', {
		'history': item
	})
