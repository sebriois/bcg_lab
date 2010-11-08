# coding: utf-8
from django import forms

from order_manager.product.models import Product
from order_manager.provider.models import Provider

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product

class ProductFilterForm(forms.Form):
  PRODUCT_CHOICES = ";".join( [ unicode(p) for p in Product.objects.all() ] )
  
  providers  = forms.ModelMultipleChoiceField(
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
                  required = False
               )

