from django.conf.urls.defaults import *

from order.views import index, item, delete, new
from order.cart_views import cart_index, cart_empty
from order.cart_views import cart_validate, cart_remove

urlpatterns = patterns('',
  # Order
  url(r'^new/$', new, name="order_new"),
  url(r'^(?P<order_id>\d+)/delete/$', delete, name="order_delete"),
  url(r'^(?P<order_id>\d+)/$', item, name="order_item"),
  url(r'^$', index, name="order_index"),
  
  # Cart
  url(r'^cart/(?P<cart_id>\d+)/empty/$', cart_empty, name="cart_empty"),
  url(r'^cart/(?P<cart_id>\d+)/provider/(?P<provider_id>\d+)/validate/$', cart_validate, name="cart_validate"),
  url(r'^cart/(?P<cart_id>\d+)/product/(?P<product_id>\d+)/remove/$', cart_remove, name="cart_remove"),
  url(r'^cart/$', cart_index, name="cart_index")
)
