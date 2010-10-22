# coding: utf-8
from django.forms import ModelForm

from order_manager.product.models import Product

class ProductForm(ModelForm):
    class Meta:
        model = Product