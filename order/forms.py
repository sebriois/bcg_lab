# coding: utf-8
from django.forms import ModelForm

from order.models import Order

class OrderForm(ModelForm):
    class Meta:
        model = Order