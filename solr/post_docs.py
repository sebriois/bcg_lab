#!/usr/bin/env python

from django.conf import settings
from product.models import Product

"""
<field name="id"            type="string"       indexed="true" stored="true" required="true"  multiValued="false" />
<field name="product"       type="text_en"      indexed="true" stored="true" required="true"  multiValued="false" />
<field name="reference"     type="text_general" indexed="true" stored="true" required="true"  multiValued="false" />
<field name="provider"      type="text_general" indexed="true" stored="true" required="true"  multiValued="false" />
<field name="origin"        type="text_general" indexed="true" stored="true" required="false"  multiValued="false" />
<field name="packaging"     type="text_general" indexed="true" stored="true" required="false"  multiValued="false" />
<field name="offer_nb"      type="text_general" indexed="true" stored="true" required="false"  multiValued="false" />
<field name="nomenclature"  type="text_general" indexed="true" stored="true" required="false"  multiValued="false" />
<field name="category"      type="text_general" indexed="true" stored="true" required="false"  multiValued="false" />
<field name="sub_category"  type="text_general" indexed="true" stored="true" required="false"  multiValued="false" />
"""

for product in Product.objects.all():
    product.post_to_solr()
