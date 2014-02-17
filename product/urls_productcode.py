from django.conf.urls import *

from product.views_productcode import autocomplete_product_codes
from product.views_productcode import import_product_codes

urlpatterns = patterns('',
  url(r'^autocomplete-codes/$', autocomplete_product_codes, name="autocomplete_product_codes"),
  url(r'^import/$', import_product_codes, name="import_product_codes"),
)
