# coding: utf-8
from django import forms

from provider.models import Provider

class ProviderForm(forms.ModelForm):
  class Meta:
    model = Provider
    exclude = ('is_local',)
  


class ImportForm(forms.Form):
    """
    Form for updating a provider's products by importing a csv file.
    """
    csv_file = forms.FileField(label=u"Fichier à importer")
