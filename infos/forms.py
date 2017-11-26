# coding: utf-8
from django import forms
from django.forms import widgets

from infos.models import Info


class InfoForm(forms.ModelForm):
    class Meta:
        model = Info
        fields = ['text', 'expiry']
        widgets = {
            'expiry': widgets.DateInput(attrs={'class':'datepicker'})
        }
