# encoding: utf-8
from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render
from django.shortcuts import get_object_or_404, redirect

from order.models import Order, OrderItem
from order.forms import ServiceForm

from bcg_lab.constants import *
from utils import *

@login_required
@transaction.commit_on_success
def tab_services(request):
    try:
        member = request.user.teammember_set.get()
    except:
        error_msg( request, u"Vous devez appartenir à une équipe pour accéder à cette page" )
        return redirect( request.META.get('HTTP_REFERER', 'home') )
    
    if request.method == 'GET':
        form = ServiceForm( member = member )
    elif request.method == 'POST':
        data = request.POST.copy()
        
        if not request.user.has_perm('order.custom_order_any_team') and not request.user.has_perm('custom_goto_status_4'):
            data['team'] = member.team.id
        
        form = ServiceForm( member = member, data = data )
        if form.is_valid():
            data = form.cleaned_data
            
            order = Order.objects.create(
                team            = data['team'],
                provider        = data['provider'],
                is_confidential = data['confidential']
            )
            
            order_item = OrderItem.objects.create(
                username        = request.user.username,
                name            = data['name'],
                price           = data['cost'],
                cost_type       = DEBIT,
                quantity        = data['quantity'],
                is_confidential = data['confidential']
            )
            
            # Add item to order
            order.items.add(order_item)
            
            return redirect('tab_cart')
    
    return render(request, "tab_services.html", {
        'form': form
    })
