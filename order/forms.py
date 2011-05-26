# coding: utf-8
from django import forms

from order.models import OrderItem

class OrderItemForm(forms.ModelForm):
  class Meta:
    model = OrderItem
    exclude = ('product_id', 'cost_type')
  
