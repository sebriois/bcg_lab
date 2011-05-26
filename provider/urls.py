from django.conf.urls.defaults import *

from provider.views import index, item, delete, new
from provider.csv_import import import_csv, export_csv, perform_import_csv

urlpatterns = patterns('',
  url(r'^new/$', new, name="provider_new"),
  url(r'^(?P<provider_id>\d+)/delete/$', delete, name="provider_delete"),
  url(r'^(?P<provider_id>\d+)/import-products/$', import_csv, name="import_products"),
  url(r'^(?P<provider_id>\d+)/perform-import-products/$', perform_import_csv, name="perform_import_products"),
  url(r'^(?P<provider_id>\d+)/export-products/$', export_csv, name="export_products"),
  url(r'^(?P<provider_id>\d+)/$', item, name="provider_item"),
  url(r'^$', index, name="provider_index")
)
