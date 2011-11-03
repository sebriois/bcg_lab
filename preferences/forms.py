# coding: utf-8
from django import forms
from django.contrib.auth.models import User

from team.models import Team, TeamMember

class UserPrefForm(forms.ModelForm):
	class Meta:
		model = User
		fields = ('first_name', 'last_name', 'email')

class EmailPrefForm(forms.ModelForm):
	class Meta:
		model = TeamMember
		fields = ('send_on_edit', 'send_on_validation', 'send_on_sent')
