# coding: utf-8
from django import forms

from team.models import Team
from provider.models import Provider
from utils import *

class HistoryFilterForm(forms.Form):
	TEAM_CHOICES = [(team.name,team.name) for team in Team.objects.all()]
	PROVIDER_CHOICES = [(p.name, p.name) for p in Provider.objects.all()]
	
	connector = forms.TypedChoiceField(
		choices = [("OR", u"l'une des"), ("AND",u"toutes les")],
		initial = "AND",
		coerce = str,
		empty_value = None,
		required = True
	)
	
	team = forms.ChoiceField(
		label			= "Equipe",
		choices		= [("","---------")] + TEAM_CHOICES,
		required	= False
	)
	
	provider = forms.ChoiceField(
		label			= "Fournisseur",
		choices		= [("","---------")] + PROVIDER_CHOICES,
		required	= False
	)
	
	date_created__gte = forms.DateField( 
		label					= "Date d'enregistrement min",
		input_formats = ["%d/%m/%Y"],
		widget				= forms.TextInput( attrs = { 'class' : 'datepicker maxToday' }),
		required			= False
	)
	
	date_created__lte = forms.DateField( 
		label					= "Date d'enregistrement max",
		input_formats = ["%d/%m/%Y"],
		widget				= forms.TextInput( attrs = { 'class' : 'datepicker maxToday' }),
		required			= False
	)
	
	def __init__(self, user, *args, **kwargs):
		super( HistoryFilterForm, self ).__init__(*args, **kwargs)
		
		if is_super_validator(user) or is_secretary(user):
			team_choices = [("","---------")] + [(team.name,team.name) for team in Team.objects.all()]
		else:
			team_choices = [("","---------")] + [(team.name,team.name) for team in get_teams(user)]
		
		self.fields['team'].choices = team_choices
		# TODO:
		# self.fields['team'].initial = get_teams(user)[0].name
	
