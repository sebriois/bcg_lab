from django.urls import path

from product.views import index, item, delete, new, edit_list, autocomplete
from product.views import export_xls

app_name = 'product'
urlpatterns = [
  path('new/$', new, name="product_new"),
  path('autocomplete/$', autocomplete, name="autocomplete_products"),
  path('edit-list/$', edit_list, name="product_edit_list"),
  path('export-to-excel/$', export_xls, name="product_export_xls"),
  path('<int:product_id>/delete/$', delete, name="product_delete"),
  path('<int:product_id>/$', item, name="product_item"),
  path('$', index, name="product_index")
]
