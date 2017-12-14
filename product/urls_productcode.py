from django.urls import path

from product.views_productcode import autocomplete_product_codes
from product.views_productcode import import_product_codes

app_name = 'product_code'
urlpatterns = [
    path('autocomplete-codes/', autocomplete_product_codes, name="autocomplete"),
    path('import/', import_product_codes, name="import"),
]
