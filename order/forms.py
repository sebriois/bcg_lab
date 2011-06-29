# coding: utf-8
from django import forms

from order.models import OrderItem
from constants import *

class OrderItemForm(forms.ModelForm):
	class Meta:
		model = OrderItem
		exclude = ('product_id', 'cost_type')
	
class AddCreditForm(forms.ModelForm):
	class Meta:
		model = OrderItem
		fields = ("name", "provider", "offer_nb", "price", "quantity", "cost_type")
		widgets	= {
			'name': forms.TextInput( attrs = {
										'class' : 'autocomplete',
										'choices': CREDIT_ORDER_CHOICES
									}),
			'cost_type': forms.HiddenInput( attrs = { 'value': CREDIT } )
		}
	
class AddDebitForm(forms.ModelForm):
	class Meta:
		model = OrderItem
		fields = ("name", "provider", "offer_nb", "price", "quantity", "cost_type")
		widgets	= {
			'name': forms.TextInput( attrs = {
										'class' : 'autocomplete',
										'choices': DEBIT_ORDER_CHOICES
									}),
			'cost_type': forms.HiddenInput( attrs = { 'value': DEBIT } )
		}
	
