from django.conf.urls.defaults import *

from order.views import order_detail, order_delete
from order.views import set_delivered, set_next_status
from order.views import cart_add, cart_empty, set_item_quantity

from order.views import tab_cart, tab_orders, tab_validation

urlpatterns = patterns('',
  # Order
  url(r'^(?P<order_id>\d+)/delete/$', order_delete, name="order_delete"),
  url(r'^(?P<order_id>\d+)/set-as-delivered/$', set_delivered, name="order_delivered"),
  url(r'^(?P<order_id>\d+)/set-next-status/$', set_next_status, name="set_next_status"),
  url(r'^(?P<order_id>\d+)/$', order_detail, name="order_item"),
  
  # Cart
  url(r'^cart/add/(?P<product_id>\d+)/(?P<quantity>\d+)$', cart_add, name="cart_add"),
  url(r'^cart/(?P<item_id>\d+)/set-quantity/(?P<quantity>\d+)$', set_item_quantity, name="set_cart_quantity"),
  url(r'^cart/empty/$', cart_empty, name="cart_empty"),
  
  # Tabs
  url(r'^validation/$', tab_validation, name="tab_validation"),
  url(r'^cart/$', tab_cart, name="tab_cart"),
  url(r'^$', tab_orders, name="tab_orders")
)
