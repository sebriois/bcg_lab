# coding: utf-8
from django import forms

from order.models import OrderItem
from team.models import Team
from provider.models import Provider
from constants import *

class OrderItemForm(forms.ModelForm):
	class Meta:
		model = OrderItem
		exclude = ('product_id', 'cost_type')
	
class AddCreditForm(forms.ModelForm):
	class Meta:
		model = OrderItem
		fields = ("name", "provider", "offer_nb", "price", "quantity", "cost_type")
		widgets = {
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
	
class ServiceForm(forms.Form):
	team = forms.ModelChoiceField( label = u"Equipe", queryset = Team.objects.all() )
	provider = forms.ModelChoiceField( label = u"Type de service", queryset = Provider.objects.filter(is_service = True) )
	name = forms.CharField( label = u"Désignation" )
	cost = forms.CharField( label = u"Montant" )
	quantity = forms.IntegerField( label = u"Quantité", initial = 1 )
	confidential = forms.BooleanField( label = u"Confidentiel ?", initial = False, required = False )
	
	def __init__(self, member, *args, **kwargs):
		super( ServiceForm, self ).__init__( *args, **kwargs )
		
		if member.team.name.upper() != "GESTION":
			self.fields['team'].initial = member.team
			self.fields['team'].widget.attrs.update({ 'disabled': 'disabled' })
	
