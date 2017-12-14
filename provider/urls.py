from django.urls import path

from provider.views import index, item, delete, new, set_notes
from provider.import_xls import import_xls, do_import
from provider.export_xls import export_xls

app_name = 'provider'
urlpatterns = [
  path('new/', new, name="provider_new"),
  path('<int:provider_id>/set-notes/', set_notes, name="set_notes"),
  path('<int:provider_id>/delete/', delete, name="provider_delete"),
  path('<int:provider_id>/import-products/', import_xls, name="import_products"),
  path('<int:provider_id>/perform-import-products/', do_import, name="perform_import_products"),
  path('<int:provider_id>/export-products/', export_xls, name="export_products"),
  path('<int:provider_id>/', item, name="provider_item"),
  path('', index, name="provider_index")
]