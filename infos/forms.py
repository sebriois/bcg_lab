# coding: utf-8
from django import forms

from infos.models import Info

class InfoForm(forms.ModelForm):
	class Meta:
		model = Info
		fields = ('text', 'expiry')
	
