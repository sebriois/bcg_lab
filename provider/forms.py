# coding: utf-8
from django.forms import ModelForm

from provider.models import Provider

class ProviderForm(ModelForm):
    class Meta:
        model = Provider
    
