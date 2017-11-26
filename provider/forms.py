# coding: utf-8
import os

from django import forms
from django.forms import widgets

from provider.models import Provider

class ProviderForm(forms.ModelForm):
    class Meta:
        model = Provider
        fields = ['name', 'users_in_charge', 'reseller', 'notes', 'is_local', 'is_service', 'direct_reception']

    def __init__( self, user, *args, **kwargs ):
        super( ProviderForm, self ).__init__( *args, **kwargs )

        if not user.has_perm('team.custom_is_admin'):
            del self.fields['is_local']

        self.fields['reseller'].queryset = Provider.objects.exclude(is_service = True).exclude(is_local = True)


class ImportForm(forms.Form):
    xls_file = forms.FileField( label = u"Fichier à importer" )
    replace_all = forms.BooleanField(
        label = u"Ecraser tous les produits existants",
        initial = False,
        required = False
    )
    offer_nb = forms.CharField(
        label = "Offre",
        required = False
    )
    expiry = forms.CharField(
        label = "Date d'expiration",
        required = False
    )
    def __init__(self, *args, **kwargs):
        super( ImportForm, self ).__init__( *args, **kwargs )
        self.fields['expiry'].widget = widgets.DateInput(attrs={'class':'datepicker'})

    def clean_expiry(self):
        offer_nb = self.data.get('offer_nb', None)
        expiry = self.cleaned_data.get('expiry', None)

        if offer_nb and not expiry:
            raise forms.ValidationError(u"Veuillez donner une date d'expiration pour cette offre.")

        return expiry

    def clean_xls_file(self):
        xls_file = self.cleaned_data['xls_file']
        extension = os.path.splitext( xls_file.name )[1]
        if not extension == '.xls':
            raise forms.ValidationError( u"%s n'est pas un fichier excel valide. Veuillez vérifier que votre fichier est au format excel (.xls)" % xls_file.name )
        else:
            return xls_file
