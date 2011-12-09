# coding: utf-8
from django import forms

from order.models import OrderItem, OrderComplement
from team.models import Team
from provider.models import Provider

from constants import *
from utils import in_team_secretary

class OrderItemForm(forms.ModelForm):
	class Meta:
		model = OrderItem
		exclude = ('product_id', 'cost_type')
	

CREDIT_ORDER_CHOICES=";".join([c.name for c in OrderComplement.objects.filter(type_comp=CREDIT)])
class AddCreditForm(forms.ModelForm):
	class Meta:
		model = OrderItem
		fields = ("name", "reference", "offer_nb", "price", "quantity", "cost_type")
		widgets = {
			'name': forms.TextInput( attrs = {
										'class' : 'autocomplete',
										'choices': CREDIT_ORDER_CHOICES
									}),
			'cost_type': forms.HiddenInput( attrs = { 'value': CREDIT } )
		}
	

DEBIT_ORDER_CHOICES=";".join([c.name for c in OrderComplement.objects.filter(type_comp=DEBIT)])
class AddDebitForm(forms.ModelForm):
	class Meta:
		model = OrderItem
		fields = ("name", "reference", "offer_nb", "price", "quantity", "cost_type")
		widgets	= {
			'name': forms.TextInput( attrs = {
										'class' : 'autocomplete',
										'choices': DEBIT_ORDER_CHOICES
									}),
			'cost_type': forms.HiddenInput( attrs = { 'value': DEBIT } )
		}
	

class ServiceForm(forms.Form):
	team = forms.ModelChoiceField( label = u"Equipe", queryset = Team.objects.all() )
	provider = forms.ModelChoiceField(
		label = u"Type de service", 
		queryset = Provider.objects.filter(is_service = True),
		empty_label = None
	)
	name = forms.CharField( label = u"Désignation" )
	cost = forms.CharField( label = u"Montant" )
	quantity = forms.IntegerField( label = u"Quantité", initial = 1 )
	confidential = forms.BooleanField( label = u"Confidentiel ?", initial = False, required = False )
	
	def __init__(self, member, *args, **kwargs):
		super( ServiceForm, self ).__init__( *args, **kwargs )
		
		if not in_team_secretary(member.user):
			self.fields['team'].initial = member.team
			self.fields['team'].widget.attrs.update({ 'disabled': 'disabled' })
	
