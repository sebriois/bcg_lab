from django.conf.urls.defaults import *

from order.views import order_detail, orderitem_detail, order_delete
from order.views import set_delivered, set_budget, set_next_status
from order.views import add_orderitem, del_orderitem
from order.views import cart_add, cart_empty, set_item_quantity

from order.views import tab_cart, tab_orders, tab_validation

urlpatterns = patterns('',
  # Order
  url(r'^(?P<order_id>\d+)/delete/$', order_delete, name="order_delete"),
  url(r'^(?P<order_id>\d+)/set-as-delivered/$', set_delivered, name="order_delivered"),
  url(r'^(?P<order_id>\d+)/set-budget/$', set_budget, name="order_budget"),
  url(r'^(?P<order_id>\d+)/set-next-status/$', set_next_status, name="set_next_status"),
  url(r'^(?P<order_id>\d+)/add-item/$', add_orderitem, name="add_orderitem"),
  url(r'^(?P<order_id>\d+)/$', order_detail, name="order_item"),
  
  # Order Items
  url(r'^(?P<orderitem_id>\d+)/del-item/$', del_orderitem, name="orderitem_delete"),
  url(r'^(?P<orderitem_id>\d+)/edit/$', orderitem_detail, name="orderitem_detail"),
  
  # Cart
  url(r'^add-to-cart/$', cart_add, name="cart_add"),
  url(r'^set-item-quantity/$', set_item_quantity, name="set_item_quantity"),
  url(r'^empty-cart/$', cart_empty, name="cart_empty"),
  
  # Tabs
  url(r'^validation/$', tab_validation, name="tab_validation"),
  url(r'^cart/$', tab_cart, name="tab_cart"),
  url(r'^$', tab_orders, name="tab_orders")
)
