from django.conf.urls.defaults import *

from order_manager.order.views import index, item, delete, new
from order_manager.order.cart_views import cart_index, cart_empty

urlpatterns = patterns('',
  # Order
  url(r'^new/$', new, name="order_new"),
  url(r'^(?P<order_id>\d+)/delete/$', delete, name="order_delete"),
  url(r'^(?P<order_id>\d+)/$', item, name="order_item"),
  url(r'^$', index, name="order_index"),
  
  # Cart
  url(r'^cart/(?P<cart_id>\d+)/empty/$', cart_empty, name="cart_empty"),
  url(r'^cart/$', cart_index, name="cart_index")
)
