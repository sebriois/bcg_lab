# coding: utf-8
from django import forms

from product.models import Product
from provider.models import Provider

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product

class ProductFilterForm(forms.Form):
  PRODUCT_CHOICES = ";".join( [ unicode(p) for p in Product.objects.all() ] )
  
  providers  = forms.ModelChoiceField(
                  label = u"Fournisseur",
                  queryset = Provider.objects.all(),
                  required = False
               )
  product    = forms.CharField(
                  label   = u"Produit",
                  widget  = forms.TextInput( attrs = {
                    'class' : 'autocomplete',
                    'choices': PRODUCT_CHOICES
                  }),
                  help_text = "Appuyez sur 'Esc' pour fermer la liste de choix.",
                  required = False
               )

