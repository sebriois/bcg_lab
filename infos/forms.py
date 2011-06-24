# coding: utf-8
from django import forms

from infos.models import Info

class InfoForm(forms.ModelForm):
	class Meta:
		model = Info
		fields = ('text',)
	
	expiry = forms.DateField( 
		label         = "Date d'expiration",
		input_formats = ["%d/%m/%Y"],
		widget        = forms.TextInput( attrs = { 'class' : 'datepicker' }),
		required      = False
	)

