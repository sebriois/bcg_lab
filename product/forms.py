# coding: utf-8
from django import forms
from django.forms import widgets

from product.models import Product, ProductType, ProductSubType
from provider.models import Provider
from constants import *

class ProductForm(forms.ModelForm):
	class Meta:
			model = Product
			widgets = {
				'expiry': widgets.DateInput(attrs={'class':'datepicker'})
			}
	
	def __init__( self, provider = None, *args, **kwargs ):
		super( ProductForm, self ).__init__( *args, **kwargs )
		
		self.fields['provider'].queryset = Provider.objects.exclude(is_service = True)
		
		if provider:
			self.fields['provider'].widget.attrs.update({'disabled':'disabled'})
			self.fields['provider'].initial = provider
		
	def clean_expiry(self):
		offer_nb = self.data.get('offer_nb', None)
		expiry = self.cleaned_data.get('expiry', None)
		
		if offer_nb and not expiry:
			raise forms.ValidationError(u"Veuillez donner une date d'expiration pour cette offre.")
		
		return expiry

class ProductFilterForm(forms.Form):
	connector = forms.TypedChoiceField(
		choices 		= [("OR", u"l'une des"), ("AND",u"toutes les")],
		initial 		= "AND",
		coerce 			= str,
		empty_value = None,
		required 		= True
	)
	provider = forms.ModelChoiceField( 
		label			= u"Fournisseur",
		queryset	= Provider.objects.exclude(is_service = True),
		required	= False
	)
	name__icontains = forms.CharField(
		label			= u"Produit",
		widget		= forms.TextInput( attrs = { 'class' : 'autocomplete' }),
								# autocomplete choices are set below, in __init__ method
		help_text	= "Appuyez sur 'esc' pour fermer la liste de choix.",
		required 	= False
	)
	reference = forms.CharField(
		label			= u"Référence",
		widget		= forms.TextInput( attrs = {
			'class' : 'autocomplete',
			'choices': EMPTY_SEL
		}),
		help_text = "Appuyez sur 'esc' pour fermer la liste de choix.",
		required 	= False
	)
	origin = forms.CharField(
		label			= u"Fournisseur d'origine",
		widget		= forms.TextInput( attrs = {
			'class' : 'autocomplete',
			'choices': EMPTY_SEL
		}),
		help_text = "Appuyez sur 'esc' pour fermer la liste de choix.",
		required 	= False
	)
	nomenclature = forms.CharField(
		label			= u"Nomenclature",
		required	= False
	)
	category = forms.ModelChoiceField(
		label			= u"Type",
		queryset	= ProductType.objects.all(),
		required	= False
	)
	sub_category = forms.ModelChoiceField(
		label			= u"Sous-type",
		queryset	= ProductSubType.objects.all(),
		required	= False
	)
	
	def __init__(self, product_choices, *args, **kwargs):
		super( ProductFilterForm, self ).__init__( *args, **kwargs )
		self.fields['name__icontains'].widget.attrs.update({'choices': product_choices})
		
		ORIGIN_CHOICES = ";".join( set([ unicode(p.origin) for p in Product.objects.all() ]) )
		self.fields['origin'].widget.attrs.update({'choices': ORIGIN_CHOICES})
		
		REFERENCE_CHOICES = ";".join( [ unicode(p.reference) for p in Product.objects.all() ] )
		self.fields['reference'].widget.attrs.update({'choices': REFERENCE_CHOICES})
	

class EditListForm(forms.Form):
	category = forms.ModelChoiceField(
		label = u"Type",
		queryset = ProductType.objects.all(),
		required = False,
		empty_label = 'Aucun'
	)
	sub_category = forms.ModelChoiceField(
		label = u"Sous-type",
		queryset = ProductSubType.objects.all(),
		required = False,
		empty_label = 'Aucun'
	)
	nomenclature = forms.CharField(
		label = "Nomenclature",
		required = False
	)
	offer_nb = forms.CharField(
		label = "Offre",
		required = False
	)
	expiry = forms.DateField(
		label = "Date d'expiration",
		input_formats = ["%d/%m/%Y"],
		widget				= forms.TextInput( attrs = { 'class' : 'datepicker' }),
		required = False
	)
	percent_raise = forms.DecimalField(
		label = "Augmentation du prix (%)",
		min_value = 0,
		max_value = 100,
		required = False
	)
	
	def clean_expiry(self):
		offer_nb = self.data.get('offer_nb', None)
		expiry = self.cleaned_data.get('expiry', None)
		
		if offer_nb and not expiry:
			raise forms.ValidationError(u"Veuillez donner une date d'expiration pour cette offre.")
		
		return expiry
	
