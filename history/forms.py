# coding: utf-8
from django import forms

from team.models import Team
from provider.models import Provider
from product.models import Product
from history.models import History
from utils import *
from constants import *

class HistoryFilterForm(forms.Form):
	PROVIDER_CHOICES = [(p.name, p.name) for p in Provider.objects.exclude(is_service = True)]
	ORIGIN_CHOICES = ";".join( set([ unicode(p.origin) for p in Product.objects.all() ]) )
	
	connector = forms.TypedChoiceField(
		choices = [("OR", u"l'une des"), ("AND",u"toutes les")],
		initial = "AND",
		coerce = str,
		empty_value = None,
		required = True
	)
	
	team = forms.ChoiceField(
		label			= "Equipe",
		choices		= EMPTY_SEL,
		required	= False
	)

	items__name = forms.CharField(
		label			= u"Produit",
		help_text	= "Appuyez sur 'esc' pour fermer la liste de choix.",
		required 	= False
	)
	
	items__reference = forms.CharField(
		label			= u"Référence",
		help_text = "Appuyez sur 'esc' pour fermer la liste de choix.",
		required 	= False
	)
	
	provider = forms.ChoiceField(
		label			= "Fournisseur",
		choices		= EMPTY_SEL + PROVIDER_CHOICES,
		required	= False
	)
	items__origin = forms.CharField(
		label			= u"Fournisseur d'origine",
		widget		= forms.TextInput( attrs = {
			'class' : 'autocomplete',
			'choices': ORIGIN_CHOICES
		}),
		help_text = "Appuyez sur 'esc' pour fermer la liste de choix.",
		required 	= False
	)
	
	date_delivered__gte = forms.DateField( 
		label					= "Date d'enregistrement min",
		input_formats = ["%d/%m/%Y"],
		widget				= forms.TextInput( attrs = { 'class' : 'datepicker maxToday' }),
		required			= False
	)
	
	date_delivered__lte = forms.DateField( 
		label					= "Date d'enregistrement max",
		input_formats = ["%d/%m/%Y"],
		widget				= forms.TextInput( attrs = { 'class' : 'datepicker maxToday' }),
		required			= False
	)
	
	def __init__(self, user, *args, **kwargs):
		super( HistoryFilterForm, self ).__init__(*args, **kwargs)
		
		if user.has_perm('team.view_all_teams'):
			teams = [t.name for t in Team.objects.all()]
		else:
			teams = [t.name for t in get_teams(user)]
			
		team_choices = [(name,name) for name in teams]
		name_choices = []
		ref_choices = []
		for h in History.objects.filter( team__in = teams ):
			for i in h.items.all():
				if i.name and not i.name in name_choices:
					name_choices.append(i.name)
				if i.reference and not i.reference in ref_choices:
					ref_choices.append(i.reference)
		
		self.fields['team'].choices = EMPTY_SEL + team_choices
		self.fields['items__reference'].widget = forms.TextInput( attrs={
			'class' : 'autocomplete',
			'choices': ";".join(ref_choices)
		})
		self.fields['items__name'].widget = forms.TextInput( attrs={
			'class' : 'autocomplete',
			'choices': ";".join(name_choices)
		})
	
