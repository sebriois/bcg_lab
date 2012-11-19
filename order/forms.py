# coding: utf-8
from decimal import Decimal, InvalidOperation

from django import forms

from order.models import OrderItem, OrderComplement
from team.models import Team
from provider.models import Provider
from product.models import Product

from constants import *
from utils import in_team_secretary

class OrderItemForm(forms.ModelForm):
	class Meta:
		model = OrderItem
		exclude = ('product_id', 'cost_type')
	

CREDIT_ORDER_CHOICES=";".join([c.name for c in OrderComplement.objects.filter(type_comp=CREDIT)])
class AddCreditForm(forms.ModelForm):
	price = forms.CharField( label = u"Montant" )
	
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
	
	def clean_price(self):
		price = self.cleaned_data.get('price', None)
		try:
			price = Decimal(price.replace(',','.'))
		except InvalidOperation:
			raise forms.ValidationError(u"Veuillez saisir un montant positif.")
		
		if price <= 0:
			raise forms.ValidationError(u"Veuillez saisir un montant positif.")
		
		return price
	


DEBIT_ORDER_CHOICES=";".join([c.name for c in OrderComplement.objects.filter(type_comp=DEBIT)])
class AddDebitForm(forms.ModelForm):
	price = forms.CharField( label = u"Montant" )
	
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
	
	def clean_price(self):
		price = self.cleaned_data.get('price', None)
		try:
			price = Decimal(price.replace(',','.'))
		except InvalidOperation:
			raise forms.ValidationError(u"Veuillez saisir un montant positif.")
		
		if price <= 0:
			raise forms.ValidationError(u"Veuillez saisir un montant positif.")
		
		return price
	

class FilterForm(forms.Form):
	connector = forms.TypedChoiceField(
		choices = [("AND",u"toutes les"), ("OR", u"l'une des")],
		initial = "AND",
		coerce = str,
		empty_value = None,
		required = True
	)

	team = forms.ModelChoiceField(
		queryset = Team.objects.all(),
		label    = "Equipe",
		required = False
	)
	
	number = forms.CharField(
		label    = u"N°cmde",
		required = False
	)
	
	provider = forms.ModelChoiceField(
		queryset = Provider.objects.exclude( is_local = True ),
		label    = "Fournisseur",
		required = False
	)
        notes = forms.CharField(
                label    = u"Commentaire",
                required = False
        )
	
	items__name__icontains = forms.CharField(
		label			= u"Produit",
		widget		= forms.TextInput( attrs = { 'class' : 'autocomplete' }),
								# autocomplete choices are set below, in __init__ method
		required 	= False
	)
	
	def __init__(self, *args, **kwargs):
		super( FilterForm, self ).__init__( *args, **kwargs )
		NAME_CHOICES = ";".join(Product.objects.all().values_list("name",flat=True))
		self.fields['items__name__icontains'].widget.attrs.update({'choices': NAME_CHOICES})
	

class ServiceForm(forms.Form):
	team = forms.ModelChoiceField(
		label = u"Equipe",
		queryset = Team.objects.all()
	)
	provider = forms.ModelChoiceField(
		label = u"Type de service", 
		queryset = Provider.objects.filter(is_service = True),
		required = True
	)
	name = forms.CharField( label = u"Désignation" )
	cost = forms.CharField( label = u"Montant" )
	quantity = forms.IntegerField( label = u"Quantité", initial = 1 )
	confidential = forms.BooleanField( label = u"Confidentiel ?", initial = False, required = False )
	
	def __init__(self, member, *args, **kwargs):
		super( ServiceForm, self ).__init__( *args, **kwargs )
		
		if not member.user.has_perm("order.custom_order_any_team"):
			self.fields['team'].initial = member.team
			self.fields['team'].widget.attrs.update({ 'disabled': 'disabled' })
	
	def clean_cost(self):
		cost = self.cleaned_data.get('cost', None)
		try:
			cost = Decimal(cost.replace(',','.'))
		except InvalidOperation:
			raise forms.ValidationError(u"Veuillez saisir un montant positif.")
		
		if cost <= 0:
			raise forms.ValidationError(u"Veuillez saisir un montant positif.")
		
		return cost
	

