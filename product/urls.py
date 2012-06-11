from django.conf.urls.defaults import *

from product.views import index, item, delete, new, edit_list
from product.views import export_xls

urlpatterns = patterns('',
  url(r'^new/$', new, name="product_new"),
  url(r'^edit-list/$', edit_list, name="product_edit_list"),
  url(r'^export-to-excel/$', export_xls, name="product_export_xls"),
  url(r'^(?P<product_id>\d+)/delete/$', delete, name="product_delete"),
  url(r'^(?P<product_id>\d+)/$', item, name="product_item"),
  url(r'^$', index, name="product_index")
)
