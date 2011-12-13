# encoding: utf-8
from django.db.models.query import Q
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.views.generic.simple import direct_to_template

from history.models import History
from history.forms import HistoryFilterForm
from order.models import OrderItem

from constants import *
from utils import *

@login_required
def index(request):
	# Get initial history_list
	if request.user.has_perm('team.custom_view_teams'):
		history_list = History.objects.all()
	else:
		team_names = [t.name for t in get_teams(request.user)]
		history_list = History.objects.filter( team__in = team_names )
	
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
	if search_name or search_ref:
		display = "by_product"
		items_id = []
		for h in history_list:
			for item in h.items.all():
				if item.id in items_id: continue
				if request.GET['connector'] == 'AND':
					if search_name and search_ref:
						if item.name == search_name and item.reference == search_ref:
							items_id.append( item.id )
					elif search_name and item.name == search_name:
						items_id.append( item.id )
					elif search_ref and item.reference == search_ref:
						items_id.append( item.id )
				elif request.GET['connector'] == 'OR':
					if search_name and item.name == search_name:
						items_id.append( item.id )
						continue
					if search_ref and item.reference == search_ref:
						items_id.append( item.id )
		objects = OrderItem.objects.filter( id__in = items_id )
	else:
		display = "by_order"
		objects = history_list
	
	return direct_to_template( request, "history/orders.html", {
		'filter_form': form,
		'objects': paginate( request, objects ),
		'display': display
	})

@login_required
def item(request, item_id):
	item = get_object_or_404( History, id = item_id )
	
	return direct_to_template( request, 'history/item.html', {
		'history': item
	})
