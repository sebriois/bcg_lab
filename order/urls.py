from django.conf.urls.defaults import *

from order.views import order_detail, orderitem_detail, order_delete, order_export
from order.views import set_delivered, set_budget, set_next_status
from order.views import add_orderitem, del_orderitem
from order.views import add_credit, add_debit
from order.views import cart_add, set_item_quantity
from order.views import set_notes, set_number, set_team
from order.views import set_is_urgent, set_has_problem
from order.views import tab_cart, tab_orders, tab_validation, tab_reception, tab_reception_local_provider

urlpatterns = patterns('',
  # Order
  url(r'^(?P<order_id>\d+)/delete/$', order_delete, name="order_delete"),
  url(r'^(?P<order_id>\d+)/set-as-delivered/$', set_delivered, name="order_delivered"),
  url(r'^(?P<order_id>\d+)/set-next-status/$', set_next_status, name="set_next_status"),
  url(r'^(?P<order_id>\d+)/set-team/$', set_team, name="order_team"),
  url(r'^(?P<order_id>\d+)/set-budget/$', set_budget, name="order_budget"),
  url(r'^(?P<order_id>\d+)/set-notes/$', set_notes, name="set_order_notes"),
  url(r'^(?P<order_id>\d+)/set-number/$', set_number, name="set_order_number"),
  url(r'^(?P<order_id>\d+)/toggle-urgent/$', set_is_urgent, name="set_is_urgent"),
  url(r'^(?P<order_id>\d+)/toggle-problem/$', set_has_problem, name="set_has_problem"),
  url(r'^(?P<order_id>\d+)/view-in-excel/$', order_export, name="order_export_xls"),
  url(r'^(?P<order_id>\d+)/add-credit/$', add_credit, name="add_credit"),
  url(r'^(?P<order_id>\d+)/add-debit/$', add_debit, name="add_debit"),
  url(r'^(?P<order_id>\d+)/add-item/$', add_orderitem, name="add_orderitem"),
  url(r'^(?P<order_id>\d+)/$', order_detail, name="order_item"),
  
  # Order Items
  url(r'^(?P<orderitem_id>\d+)/del-item/$', del_orderitem, name="orderitem_delete"),
  url(r'^(?P<orderitem_id>\d+)/edit/$', orderitem_detail, name="orderitem_detail"),
  url(r'^set-item-quantity/$', set_item_quantity, name="set_item_quantity"),
  
  # Cart
  url(r'^add-to-cart/$', cart_add, name="cart_add"),
  
  # Tabs
  url(r'^validation/$', tab_validation, name="tab_validation"),
  url(r'^cart/$', tab_cart, name="tab_cart"),
	url(r'^reception/$', tab_reception, name="tab_reception"),
	url(r'^reception-local-provider/$', tab_reception_local_provider, name="tab_reception_local_provider"),
  url(r'^$', tab_orders, name="tab_orders")
)
