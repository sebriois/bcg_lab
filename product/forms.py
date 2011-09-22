# coding: utf-8
from django import forms
from django.forms import widgets

from product.models import Product
from provider.models import Provider
from constants import CATEGORY_CHOICES, SUBCATEGORY_CHOICES

class ProductForm(forms.ModelForm):
	class Meta:
			model = Product
			widgets = {
				'expiry': widgets.DateInput(attrs={'class':'datepicker'})
			}
	
	def __init__( self, provider = None, *args, **kwargs ):
		super( ProductForm, self ).__init__( *args, **kwargs )
		
		
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
	ORIGIN_CHOICES = ";".join( set([ unicode(p.origin) for p in Product.objects.all() ]) )
	REFERENCE_CHOICES = ";".join( [ unicode(p.reference) for p in Product.objects.all() ] )
	
	connector = forms.TypedChoiceField(
		choices 		= [("OR", u"l'une des"), ("AND",u"toutes les")],
		initial 		= "AND",
		coerce 			= str,
		empty_value = None,
		required 		= True
	)
	provider = forms.ModelChoiceField( 
		label			= u"Fournisseur",
		queryset	= Provider.objects.all(),
		required	= False
	)
	name = forms.CharField(
		label			= u"Produit",
		widget		= forms.TextInput( attrs = { 'class' : 'autocomplete' }),
		help_text = "Appuyez sur 'esc' pour fermer la liste de choix.",
		required 	= False
	)
	reference = forms.CharField(
		label			= u"Référence",
		widget		= forms.TextInput( attrs = {
			'class' : 'autocomplete',
			'choices': REFERENCE_CHOICES
		}),
		help_text = "Appuyez sur 'esc' pour fermer la liste de choix.",
		required 	= False
	)
	origin = forms.CharField(
		label			= u"Fournisseur d'origine",
		widget		= forms.TextInput( attrs = {
			'class' : 'autocomplete',
			'choices': ORIGIN_CHOICES
		}),
		help_text = "Appuyez sur 'esc' pour fermer la liste de choix.",
		required 	= False
	)
	nomenclature = forms.CharField(
		label			= u"Nomenclature",
		required	= False
	)
	category = forms.TypedChoiceField(
		label			= u"Type",
		choices		= CATEGORY_CHOICES,
		coerce		= int,
		required	= False
	)
	sub_category = forms.TypedChoiceField(
		label			= u"Sous-Type",
		choices		= SUBCATEGORY_CHOICES,
		coerce		= int,
		required	= False
	)
	
	def __init__(self, product_choices, *args, **kwargs):
		super( ProductFilterForm, self ).__init__( *args, **kwargs )
		self.fields['name'].widget.attrs.update({'choices': product_choices})
	

