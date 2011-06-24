# coding: utf-8
from django import forms

from issues.models import Issue

class IssueForm(forms.ModelForm):
	class Meta:
		model = Issue
		fields = ('title', 'issue_type', 'severity', 'description')
	
