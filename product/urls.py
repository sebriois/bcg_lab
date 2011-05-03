from django.conf.urls.defaults import *

from product.views import index, item, delete, new

urlpatterns = patterns('',
  url(r'^new/$', new, name="product_new"),
  url(r'^(?P<product_id>\d+)/delete/$', delete, name="product_delete"),
  url(r'^(?P<product_id>\d+)/$', item, name="product_item"),
  url(r'^$', index, name="product_index")
)
