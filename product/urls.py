from django.conf.urls.defaults import *

from order_manager.product.views import index, item, delete, new, add_to_cart

urlpatterns = patterns('',
  url(r'^new/$', new, name="product_new"),
  # url(r'^find/$', find, name="product_find"),
  url(r'^(?P<product_id>\d+)/delete/$', delete, name="product_delete"),
  url(r'^(?P<product_id>\d+)/add-to-cart/$', add_to_cart, name="product_add_cart"),
  url(r'^(?P<product_id>\d+)/$', item, name="product_item"),
  url(r'^$', index, name="product_index")
)
