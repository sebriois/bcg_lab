# coding: utf-8
from django.forms import ModelForm

from order_manager.order.models import Order

class OrderForm(ModelForm):
    class Meta:
        model = Order