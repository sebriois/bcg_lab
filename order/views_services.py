# encoding: utf-8

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.views.generic.simple import direct_to_template
from django.shortcuts import get_object_or_404, redirect

from order.models import Order, OrderItem
from order.forms import ServiceForm

from constants import *
from utils import *

@login_required
@transaction.commit_on_success
def tab_services(request):
	member = request.user.teammember_set.get()
	
	if request.method == 'GET':
		form = ServiceForm( member = member )
	elif request.method == 'POST':
		data = request.POST.copy()
		
		if not in_team_secretary( request.user ):
			data.update({ 'team': member.team.id })
		
		form = ServiceForm( member = member, data = data )
		if form.is_valid():
			data = form.cleaned_data
			
			order = Order.objects.create(
				team 						= data['team'],
				provider 				= data['provider'],
				is_confidential = data['confidential']
			)
			
			order_item = OrderItem.objects.create(
				username				= request.user.username,
				name						= data['name'],
				price						= data['cost'],
				cost_type				= DEBIT,
				quantity				= data['quantity'],
				is_confidential	= data['confidential']
			)
			
			order.items.add(order_item)
			
			return redirect('set_next_status', order_id = order.id)
	
	return direct_to_template(request, "tab_services.html", {
		'form': form
	})
