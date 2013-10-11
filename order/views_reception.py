# encoding: utf-8
from datetime import datetime, date, timedelta
from decimal import Decimal
import xlwt

from django.db.models.query import Q
from django.db import transaction
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseServerError
from django.shortcuts import get_object_or_404, redirect
from django.template import Context, loader
from django.utils.http import urlencode
from django.shortcuts import render

from provider.models import Provider
from product.models import Product
from budget.models import Budget, BudgetLine
from order.models import Order, OrderItem
from order.forms import OrderItemForm, AddDebitForm, AddCreditForm, FilterForm

from bcg_lab.constants import *
from utils import *

@login_required
@transaction.commit_on_success
def tab_reception( request ):
    if request.method == "GET":
        orderitems = OrderItem.objects.filter(
            order__status = 4,
            order__provider__is_local = False
        ).exclude(
            product_id__isnull = True,
            order__provider__is_service = False
        ).exclude(
            order__provider__direct_reception = True
        )
        
        if not request.user.has_perm("team.custom_view_teams"):
            orderitems = orderitems.filter(
                Q(username = request.user.username) |
                Q(order__team__in = get_teams(request.user))
            )
        
        return render( request, 'order/reception.html', {
            'orderitems': orderitems.order_by('order__number', 'name')
        })
    
    elif request.method == "POST":
        action_ids = filter( lambda key: key.startswith("action_"), request.POST.keys() )
        order_ids = []
        
        for action_id in action_ids:
            item_id = action_id.split("_")[1]
            item = OrderItem.objects.get( id = item_id )
            order = item.get_order()
            
            qty_delivered = int( request.POST["delivered_%s" % item_id] )
            
            if item.delivered - qty_delivered < 0 or item.delivered - qty_delivered > item.quantity:
                if item.delivered - qty_delivered < 0:
                    error_msg( request, u"Commande %s: %s (%s) - la quantité livrée ne doit pas dépasser la quantité attendue." % (order.number, item.name, item.reference) )
                else:
                    error_msg( request, u"Commande %s: %s (%s) - la quantité à livrer ne doit pas dépasser la quantité attendue." % (order.number, item.name, item.reference) )
            else:
                item.delivered -= qty_delivered
            
            item.username_recept = request.user.username
            item.save()
        
        #
        # From here: select orders to be pushed to history
        #
        
        order_list = Order.objects.filter( status = 4 )
        
        # If user has 'local_provider' permissions
        if request.user.has_perm("order.custom_view_local_provider") and not request.user.is_superuser:
            order_list = order_list.filter( provider__is_local = True )
        
        # If user is not an admin, filter on team
        elif not request.user.has_perm("team.custom_is_admin"):
            order_list = order_list.filter( team = get_teams( request.user )[0] )
        
        # Exclude 'automatic reception' type orders
        order_list = order_list.exclude(
            provider__direct_reception = True, 
            last_change__gte = datetime.now() - timedelta(days = 7)
        )
        
        # Move to history orders having 0 item to receive
        for order in order_list:
            
            # Only consider items that are related to a product OR 
            # that are a 'service' but not under direct reception
            order_items = order.items.filter(
                Q( product_id__isnull = False ) |
                Q( order__provider__is_service = True, order__provider__direct_reception = False )
            )
            
            # If none of the items has to be delivered
            if order_items.filter( delivered__gt = 0 ).count() == 0:
                if ( not request.user.has_perm("order.custom_view_local_provider") or request.user.is_superuser ) and order.provider.direct_reception == False:
                    info_msg( request, u"La commande %s (%s) a été entièrement réceptionnée et archivée." % (order.number, order.provider.name) )
                
                order.save_to_history()
                order.delete()
        
    return redirect("tab_reception")


@login_required
@transaction.commit_on_success
def tab_reception_local_provider( request ):
    if request.method == "GET":
        orderitems = OrderItem.objects.filter(
            order__status = 4,
            order__provider__is_local = True,
            product_id__isnull = False
        )
        if not request.user.has_perm("team.custom_view_teams") and not request.user.has_perm("order.custom_view_local_provider"):
            orderitems = orderitems.filter(
                order__team = get_teams( request.user )[0]
            )
        
        return render( request, 'order/reception_local.html', {
            'orderitems': orderitems.order_by('order__team')
        })
    elif request.method == "POST":
        action_ids = filter( lambda key: key.startswith("action_"), request.POST.keys() )
        order_ids = []
        
        for action_id in action_ids:
            item_id = action_id.split("_")[1]
            item = OrderItem.objects.get( id = item_id )
            order = item.get_order()
            
            qty_delivered = int( request.POST["delivered_%s" % item_id] )
            
            if item.delivered - qty_delivered < 0 or item.delivered - qty_delivered > item.quantity:
                if item.delivered - qty_delivered < 0:
                    error_msg( request, u"Commande %s: %s (%s) - la quantité livrée ne doit pas dépasser la quantité attendue." % (order.number, item.name, item.reference) )
                else:
                    error_msg( request, u"Commande %s: %s (%s) - la quantité à livrer ne doit pas dépasser la quantité attendue." % (order.number, item.name, item.reference) )
            else:
                item.delivered -= qty_delivered
            item.save()
        
        for order in Order.objects.filter( status = 4, provider__is_local = True ):
            if order.items.filter( delivered__gt = 0, product_id__isnull = False ).count() == 0:
                order.save_to_history()
                order.delete()
    
    return redirect("tab_reception_local_provider")

