# coding: utf-8
from django import forms

from team.models import Team
from provider.models import Provider


class HistoryFilterForm(forms.Form):
  connector = forms.TypedChoiceField(
    choices = [("OR", u"l'une des"), ("AND",u"toutes les")],
    initial = "AND",
    coerce = str,
    empty_value = None,
    required = True
  )
  
  team = forms.ChoiceField(
    label     = "Equipe",
    choices   = [("","---------")] + [(team.name,team.name) for team in Team.objects.all()],
    required  = False
  )
  
  provider = forms.ChoiceField(
    label     = "Fournisseur",
    choices   = [("","---------")] + [(p.name, p.name) for p in Provider.objects.all()],
    required  = False
  )
  
  date_created__gte = forms.DateField( 
    label         = "Date d'enregistrement min",
    input_formats = ["%d/%m/%Y"],
    widget        = forms.TextInput( attrs = { 'class' : 'datepicker maxToday' }),
    required      = False
  )
  
  date_created__lte = forms.DateField( 
    label         = "Date d'enregistrement max",
    input_formats = ["%d/%m/%Y"],
    widget        = forms.TextInput( attrs = { 'class' : 'datepicker maxToday' }),
    required      = False
  )
  
  price__gte = forms.DecimalField(
    label = "Prix min",
    min_value = 0,
    max_digits = 12,
    decimal_places = 2,
    required = False
  )
  
  price__lte = forms.DecimalField(
    label = "Prix max",
    min_value = 0,
    max_digits = 12,
    decimal_places = 2,
    required = False
  )
