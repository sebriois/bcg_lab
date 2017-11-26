# encoding: utf-8
from django.db.models.query import Q
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from order.models import Order, OrderItem
from team.utils import get_teams
from utils.request_messages import info_msg, error_msg


@login_required
@transaction.atomic
def tab_reception(request):
    orderitems = OrderItem.objects.filter(order__status = 4)
    
    # Exclude items from local provider
    orderitems = orderitems.exclude(order__provider__is_local = True)
    
    # Exclude items with direct reception
    orderitems = orderitems.exclude(order__provider__direct_reception = True)
    
    # Exclude orphan products
    orderitems = orderitems.exclude(product_id__isnull = True, order__provider__is_service = False)
    
    # Only keep items ordered by request user or by its team
    if not request.user.has_perm("team.custom_view_teams"):
        orderitems = orderitems.filter(
            Q(username = request.user.username) |
            Q(order__team__in = get_teams(request.user))
    )
    
    return render(request, 'order/reception.html', {
        'orderitems': orderitems.order_by('order__number', 'name')
    })

@login_required
@transaction.atomic
def do_reception(request):
    if not request.method == "POST":
        return redirect('tab_reception')
    
    action_ids = filter(lambda key: key.startswith("action_"), request.POST.keys())
    for action_id in action_ids:
        item_id = action_id.split("_")[1]
        item    = OrderItem.objects.get(id = item_id)
        
        if Order.objects.filter(items__id = item.id).count() == 0:
            continue
        
        order = item.get_order()
        qty_delivered = int(request.POST.get("delivered_%s" % item_id, 0))
        
        if item.delivered - qty_delivered < 0:
            error_msg(request, u"Commande %s: %s (%s) - la quantité livrée ne doit pas dépasser la quantité attendue." % (order.number, item.name, item.reference))
        elif item.delivered - qty_delivered > item.quantity:
            error_msg(request, u"Commande %s: %s (%s) - la quantité à livrer ne doit pas dépasser la quantité attendue." % (order.number, item.name, item.reference))
        else:
            item.delivered -= qty_delivered
            item.username_recept = request.user.username
            item.save()
    
    #
    # From here: select orders to be pushed to history
    #
    
    order_list = Order.objects.filter(status = 4)
    order_list = order_list.exclude(provider__is_local = True)
    order_list = order_list.exclude(provider__direct_reception = True)
    
    # If user can't see all teams
    if not request.user.has_perm("team.custom_view_teams"):
        order_list = order_list.filter(team__in = get_teams(request.user))
    
    # Push orders with no delivery left to history
    for order in order_list:
        
        # Only consider items that are related to a product
        order_items = order.items.exclude(product_id__isnull = True, order__provider__is_service = False)
        
        # If there is no item left to be delivered
        if order_items.filter(delivered__gt = 0).count() == 0:
            info_msg(request, u"La commande %s (%s) a été entièrement réceptionnée et archivée." % (order.number, order.provider.name))
            order.save_to_history()
            order.delete()
    
    return redirect("tab_reception")


@login_required
@transaction.atomic
def tab_reception_local_provider(request):
    if request.method == "GET":
        orderitems = OrderItem.objects.filter(
            order__status = 4,
            order__provider__is_local = True,
            product_id__isnull = False
    )
        if not request.user.has_perm("team.custom_view_teams") and not request.user.has_perm("order.custom_view_local_provider"):
            orderitems = orderitems.filter(
                order__team = get_teams(request.user)[0]
        )
        
        return render(request, 'order/reception_local.html', {
            'orderitems': orderitems.order_by('order__team')
        })
    elif request.method == "POST":
        action_ids = filter(lambda key: key.startswith("action_"), request.POST.keys())

        for action_id in action_ids:
            item_id = action_id.split("_")[1]
            item = OrderItem.objects.get(id = item_id)
            order = item.get_order()
            
            qty_delivered = int(request.POST["delivered_%s" % item_id])
            
            if item.delivered - qty_delivered < 0 or item.delivered - qty_delivered > item.quantity:
                if item.delivered - qty_delivered < 0:
                    error_msg(request, u"Commande %s: %s (%s) - la quantité livrée ne doit pas dépasser la quantité attendue." % (order.number, item.name, item.reference))
                else:
                    error_msg(request, u"Commande %s: %s (%s) - la quantité à livrer ne doit pas dépasser la quantité attendue." % (order.number, item.name, item.reference))
            else:
                item.delivered -= qty_delivered
            item.save()
        
        for order in Order.objects.filter(status = 4, provider__is_local = True):
            if order.items.filter(delivered__gt = 0, product_id__isnull = False).count() == 0:
                order.save_to_history()
                order.delete()
    
    return redirect("tab_reception_local_provider")

