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
	team_names = []
	for team in get_teams(request.user):
		if not team.name in team_names:
			team_names.append(team.name)
	
	if is_secretary(request.user) or is_super_secretary(request.user): # admin is also a 'secretary'
		history_list = History.objects.all()
	else:
		history_list = History.objects.filter( team__in = team_names )
	
	if request.method == 'GET':
		form = HistoryFilterForm( user = request.user )
	
	elif request.method == 'POST':
		form = HistoryFilterForm( user = request.user, data = request.POST )
		
		if form.is_valid():
			data = form.cleaned_data
			
			for key, value in data.items():
				if not value:
					del data[key]
			
			Q_obj = Q()
			Q_obj.connector = data.pop("connector")
			Q_obj.children	= data.items()
			
			history_list = history_list.filter( Q_obj )
		else:
			error_msg( request, "Le formulaire n'a pas pu être validé.")
	else:
		error_msg( request, "This request method (%s) is not handled on this page" % request.method )
		return redirect( 'history' )
	
	history_list.order_by( 'date_created' )
	return direct_to_template( request, "tab_history.html", {
		'filter_form': form,
		'history': paginate( request, history_list )
	})


@login_required
def item(request, item_id):
	item = get_object_or_404( History, id = item_id )
	
	return direct_to_template( request, 'history/item.html', {
		'history': item
	})
