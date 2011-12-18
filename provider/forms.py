# coding: utf-8
import os

from django import forms

from provider.models import Provider

class ProviderForm(forms.ModelForm):
	class Meta:
		model = Provider
		exclude = ('is_local','is_service')
	


class ImportForm(forms.Form):
	xls_file = forms.FileField(label=u"Fichier à importer")
	replace_all = forms.BooleanField( label=u"Ecraser tous les produits existants", initial = False, required = False)
	
	def clean_xls_file(self):
		xls_file = self.cleaned_data['xls_file']
		extension = os.path.splitext( xls_file.name )[1]
		if not extension == '.xls':
			raise forms.ValidationError( u"%s n'est pas un fichier excel valide. Veuillez vérifier que votre fichier est au format excel (.xls)" % xls_file.name )
		else:
			return xls_file
