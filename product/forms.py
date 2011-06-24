# coding: utf-8
from django import forms

from product.models import Product
from provider.models import Provider

class ProductForm(forms.ModelForm):
		class Meta:
				model = Product
				exclude = ('expiry',)
		
		expiry = forms.DateField( 
			label         = "Date d'expiration",
			input_formats = ["%d/%m/%Y"],
			widget        = forms.TextInput( attrs = { 'class' : 'datepicker' }),
			required      = False
	  )
		
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
	PRODUCT_CHOICES = ";".join( [ unicode(p) for p in Product.objects.all() ] )
	
	provider	= forms.ModelChoiceField( label = u"Fournisseur",
								queryset	= Provider.objects.all(),
								required	= False
							)
	product		= forms.CharField( label = u"Produit",
								widget	= forms.TextInput( attrs = {
									'id' : 'autocomplete',
									'choices': PRODUCT_CHOICES
								}),
								help_text = "Appuyez sur 'esc' pour fermer la liste de choix.",
								required = False
							)

