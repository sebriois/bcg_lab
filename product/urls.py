from django.urls import path

from product.views import index, item, delete, new, edit_list, autocomplete
from product.views import export_xls

app_name = 'product'
urlpatterns = [
    path('new/', new, name = "new"),
    path('autocomplete/', autocomplete, name = "autocomplete"),
    path('edit-list/', edit_list, name = "edit_list"),
    path('export-to-excel/', export_xls, name = "export_xls"),
    path('<int:product_id>/delete/', delete, name = "delete"),
    path('<int:product_id>/', item, name = "item"),
    path('', index, name = "list")
]
