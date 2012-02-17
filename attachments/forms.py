# coding: utf-8
from django import forms

from attachments.models import Attachment

class AttachmentForm(forms.ModelForm):
	class Meta:
		model = Attachment
