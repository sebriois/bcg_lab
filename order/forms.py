# coding: utf-8
from django import forms

from order.models import Order
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
  
  team = forms.ModelChoiceField(
    label     = "Equipe",
    queryset  = Team.objects.all(),
    required  = False
  )
  
  provider = forms.ModelChoiceField(
    label     = "Fournisseur",
    queryset  = Provider.objects.all(),
    required  = False
  )
  
  date_created__gte = forms.DateField( 
    label         = "Date d'enregistrement min",
    input_formats = ["%d/%m/%Y"],
    widget        = forms.TextInput( attrs = { 'class' : 'datepicker' }),
    required      = False
  )
  
  date_created__lte = forms.DateField( 
    label         = "Date d'enregistrement max",
    input_formats = ["%d/%m/%Y"],
    widget        = forms.TextInput( attrs = { 'class' : 'datepicker' }),
    required      = False
  )
  
  date_delivered__gte = forms.DateField( 
    label         = "Date de livraison min",
    input_formats = ["%d/%m/%Y"],
    widget        = forms.TextInput( attrs = { 'class' : 'datepicker' }),
    required      = False
  )
  
  date_delivered__lte = forms.DateField( 
    label         = "Date de livraison max",
    input_formats = ["%d/%m/%Y"],
    widget        = forms.TextInput( attrs = { 'class' : 'datepicker' }),
    required      = False
  )
  
  price__gte = forms.FloatField(
    label = "Prix min",
    min_value = 0,
    required = False
  )
  
  price__lte = forms.FloatField(
    label = "Prix max",
    min_value = 0,
    required = False
  )
