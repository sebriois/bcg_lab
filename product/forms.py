# coding: utf-8
from decimal import Decimal

from django import forms
from django.forms import widgets
from django.core.urlresolvers import reverse, reverse_lazy

from product.models import Product, ProductType, ProductSubType, ProductCode
from provider.models import Provider
from bcg_lab.constants import *

class ProductCodeForm(forms.Form):
    file = forms.FileField( label = u"Fichier à importer" )

class ProductForm(forms.ModelForm):
    price = forms.CharField( label = "Prix", required = True )
    
    class Meta:
            model = Product
            widgets = {
                'expiry': widgets.DateInput(attrs={'class':'datepicker'}),
                'nomenclature': widgets.TextInput( attrs = {
                    'class': 'autocomplete',
                    'autocomplete_url': reverse_lazy('autocomplete_product_codes')
                })
            }
    
    def __init__( self, provider = None, *args, **kwargs ):
        super( ProductForm, self ).__init__( *args, **kwargs )
        
        self.fields['provider'].queryset = Provider.objects.exclude(is_service = True)
        if provider:
            self.fields['provider'].widget.attrs.update({'disabled':'disabled'})
            self.fields['provider'].initial = provider
    
    def clean_price(self):
        price = self.cleaned_data.get('price', None)
        
        try:
            price = Decimal(price.replace(",","."))
        except:
            raise forms.ValidationError(u"Veuillez saisir un nombre positif.")
        
        if not price > 0:
            raise forms.ValidationError(u"Veuillez saisir un nombre positif.")
        
        return price
    
    def clean_expiry(self):
        offer_nb = self.data.get('offer_nb', None)
        expiry = self.cleaned_data.get('expiry', None)
        
        if offer_nb and not expiry:
            raise forms.ValidationError(u"Veuillez donner une date d'expiration pour cette offre.")
        
        return expiry
    
    def clean_nomenclature(self):
        nomenclature = self.cleaned_data.get('nomenclature', None)
        if not nomenclature:
            return None

        product_code = nomenclature.split(' - ')[0]
        if ProductCode.objects.filter( code = product_code ).count() == 0:
            raise forms.ValidationError(u"Cette nomenclature (%s) n'est pas reconnue." % product_code)

        return product_code

class ProductFilterForm(forms.Form):
    connector = forms.TypedChoiceField(
        choices     = [("AND",u"toutes les"),("OR", u"l'une des")],
        initial     = "AND",
        coerce      = str,
        empty_value = None,
        required    = True
    )
    provider = forms.ModelChoiceField( 
        label    = u"Fournisseur",
        queryset = Provider.objects.exclude(is_service = True),
        required = False
    )
    name__icontains = forms.CharField(
        label    = u"Produit",
        required = False,
        widget   = widgets.TextInput( attrs = { 
            'class' : 'autocomplete', 
            'autocomplete_url': reverse_lazy('autocomplete_products') 
        }),
    )
    reference = forms.CharField(
        label    = u"Référence",
        required = False
    )
    origin = forms.ChoiceField(
        label    = u"Fournisseur d'origine",
        choices  = EMPTY_SEL + [(origin, origin) for origin in sorted(set(Product.objects.filter(origin__isnull = False).exclude(origin = "").values_list("origin",flat=True)), key = lambda i: i.lower())],
        required = False
    )
    nomenclature = forms.CharField(
        label    = u"Nomenclature",
        required = False,
        widget   = widgets.TextInput( attrs = { 
            'class' : 'autocomplete', 
            'autocomplete_url': reverse_lazy('autocomplete_product_codes') 
        }),
    )
    category = forms.ModelChoiceField(
        label    = u"Type",
        queryset = ProductType.objects.all(),
        required = False
    )
    sub_category = forms.ModelChoiceField(
        label    = u"Sous-type",
        queryset = ProductSubType.objects.all(),
        required = False
    )
    

class EditListForm(forms.Form):
    category = forms.ModelChoiceField(
        label    = u"Type",
        queryset = ProductType.objects.all(),
        required = False,
        empty_label = 'Aucun'
    )
    sub_category = forms.ModelChoiceField(
        label       = u"Sous-type",
        queryset    = ProductSubType.objects.all(),
        required    = False,
        empty_label = 'Aucun'
    )
    nomenclature = forms.CharField(
        label    = "Nomenclature",
        required = False,
        widget   = widgets.TextInput( attrs = { 
            'class' : 'autocomplete', 
            'autocomplete_url': reverse_lazy('autocomplete_product_codes') 
        }),
    )
    offer_nb = forms.CharField(
        label    = "Offre",
        required = False
    )
    expiry = forms.DateField(
        label         = "Date d'expiration",
        input_formats = ["%d/%m/%Y"],
        widget        = forms.TextInput( attrs = { 'class' : 'datepicker' }),
        required      = False
    )
    percent_raise = forms.DecimalField(
        label     = "Variation du prix (%)",
        min_value = 0,
        max_value = 100,
        required  = False
    )
    
    def clean_expiry(self):
        offer_nb = self.data.get('offer_nb', None)
        expiry = self.cleaned_data.get('expiry', None)
        
        if offer_nb and not expiry:
            raise forms.ValidationError(u"Veuillez donner une date d'expiration pour cette offre.")
        
        return expiry
    
