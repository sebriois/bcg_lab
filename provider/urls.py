from django.conf.urls.defaults import *

from provider.views import index, item, delete, new
from provider.csv_import import export_csv
from provider.import_xls import import_xls, do_import
from provider.export_xls import export_xls

urlpatterns = patterns('',
  url(r'^new/$', new, name="provider_new"),
  url(r'^(?P<provider_id>\d+)/delete/$', delete, name="provider_delete"),
  url(r'^(?P<provider_id>\d+)/import-products/$', import_xls, name="import_products"),
  url(r'^(?P<provider_id>\d+)/perform-import-products/$', do_import, name="perform_import_products"),
  url(r'^(?P<provider_id>\d+)/export-products/$', export_xls, name="export_products"),
  url(r'^(?P<provider_id>\d+)/$', item, name="provider_item"),
  url(r'^$', index, name="provider_index")
)
