# coding: utf-8
from django import forms
from django.forms import widgets
from django.urls import reverse_lazy

from bcg_lab.constants import EMPTY_SEL
from team.models import Team
from provider.models import Provider
from budget.models import Budget, BudgetLine
from order.models import OrderItem
from team.utils import get_teams


class HistoryFilterForm(forms.Form):
    connector = forms.TypedChoiceField(
        choices = [("AND",u"toutes les"), ("OR", u"l'une des")],
        initial = "AND",
        coerce = str,
        empty_value = None,
        required = True
    )
    team = forms.ModelChoiceField(
        label    = "Equipe",
        queryset = Team.objects.none(),
        required = False
    )
    comments__icontains = forms.CharField(
        label    = "Commentaire",
        required = False
    )
    items__name__icontains = forms.CharField(
        label     = u"Produit",
        required  = False,
        widget    = widgets.TextInput( attrs = {
            'class' : 'autocomplete',
            'autocomplete_url': reverse_lazy('product:autocomplete')
        })
    )
    items__reference = forms.CharField(
        label     = u"Référence",
        required  = False
    )
    items__origin = forms.CharField(
        label     = u"Fournisseur d'origine",
        required  = False
    )
    items__category = forms.ChoiceField(
        label    = "Type",
        choices  = EMPTY_SEL,
        required = False
    )
    items__sub_category = forms.ChoiceField(
        label    = "Sous-type",
        choices  = EMPTY_SEL,
        required = False
    )
    provider = forms.ModelChoiceField( 
        label    = u"Fournisseur",
        queryset = Provider.objects.all(),
        required = False
    )
    number = forms.CharField(
        label    = u"N° de commande",
        required = False,
        widget   = widgets.TextInput( attrs = {
            'class' : 'autocomplete',
            'autocomplete_url': reverse_lazy('order:autocomplete_number')
        })
    )
    date_delivered__gte = forms.DateField( 
        label         = "Date d'enregistrement min",
        input_formats = ["%d/%m/%Y"],
        widget        = widgets.TextInput( attrs = { 'class' : 'datepicker maxToday' }),
        required      = False
    )
    date_delivered__lte = forms.DateField( 
        label         = "Date d'enregistrement max",
        input_formats = ["%d/%m/%Y"],
        widget        = widgets.TextInput( attrs = { 'class' : 'datepicker maxToday' }),
        required      = False
    )
    
    def __init__(self, user, *args, **kwargs):
        super( HistoryFilterForm, self ).__init__(*args, **kwargs)
        
        if user.has_perm('team.custom_view_teams'):
            teams = Team.objects.all()
        elif user.has_perm("order.custom_view_local_provider"):
            teams = Team.objects.all()
        else:
            teams = get_teams(user)
        team_choices = []
        for team in teams:
            team_choices.append((team.id, team.fullname))
            for team_name_history in team.teamnamehistory_set.all():
                team_choice = (team.id, "%s (%s)" % (team_name_history.fullname, team.fullname))
                if team_choice not in team_choices:
                    team_choices.append(team_choice)
        self.fields['team'].queryset = teams
        self.fields['team'].widget = forms.Select(choices = EMPTY_SEL + team_choices)

        categories = list(set(OrderItem.objects.values_list('category', flat = True).order_by('category')))
        self.fields['items__category'].choices = EMPTY_SEL + [(c,c) for c in categories]
        
        sub_categories = list(set(OrderItem.objects.values_list('sub_category', flat = True).order_by('sub_category')))
        self.fields['items__sub_category'].choices = EMPTY_SEL + [(sc, sc) for sc in sub_categories]
    

class BudgetHistoryFilterForm(forms.Form):
    connector = forms.TypedChoiceField(
        choices = [("AND", u"toutes les"), ("OR", u"l'une des")],
        initial = "AND",
        coerce = str,
        empty_value = None,
        required = True
    )
    team = forms.ModelChoiceField(
        label    = u"Equipe",
        queryset = Team.objects.none(),
        required = False
    )
    budget_type = forms.ChoiceField(
        label    = "Tutelle",
        choices  = EMPTY_SEL + [(0, u"CNRS"),(1, u"UPS")],
        required = False
    )
    budget_id = forms.ChoiceField(
        label    = "Budget",
        choices  = EMPTY_SEL,
        required = False
    )
    nature = forms.ChoiceField(
        label    = "Nature",
        choices  = EMPTY_SEL,
        required = False
    )
    number = forms.CharField(
        label    = "N°cmde",
        required = False,
        widget   = widgets.TextInput( attrs = {
            'class' : 'autocomplete',
            'autocomplete_url': reverse_lazy('order:autocomplete_number')
        })
    )
    product__icontains = forms.CharField(
        label    = u"Produit",
        required = False,
        widget   = widgets.TextInput( attrs = {
            'class' : 'autocomplete',
            'autocomplete_url': reverse_lazy('product:autocomplete')
        })
    )
    provider = forms.ModelChoiceField(
        label    = "Fournisseur",
        queryset = Provider.objects.all(),
        required = False
    )
    date__gte = forms.DateField( 
        label         = "Date d'enregistrement min",
        input_formats = ["%d/%m/%Y"],
        widget        = widgets.TextInput( attrs = { 'class' : 'datepicker maxToday' }),
        required      = False
    )
    date__lte = forms.DateField( 
        label         = "Date d'enregistrement max",
        input_formats = ["%d/%m/%Y"],
        widget        = widgets.TextInput( attrs = { 'class' : 'datepicker maxToday' }),
        required      = False
    )
    
    def __init__(self, user, *args, **kwargs):
        super( BudgetHistoryFilterForm, self ).__init__(*args, **kwargs)
        
        if user.has_perm('team.custom_view_teams'):
            teams = Team.objects.all()
            budget_choices = [(b.id,b.name) for b in Budget.objects.filter(is_active=False)]
        else:
            teams = get_teams(user)
            budget_choices = [(b.id,b.name) for b in Budget.objects.filter(is_active=False, team__in = [t.id for t in teams])]
        
        number_choices = []
        for bl in BudgetLine.objects.filter(is_active = False, team__in = [t.name for t in teams]):
            if bl.number and not bl.number in number_choices:
                number_choices.append(bl.number)

        team_choices = []
        for team in teams:
            team_choices.append((team.id, team.fullname))
            for team_name_history in team.teamnamehistory_set.all():
                team_choice = (team.id, "%s (%s)" % (team_name_history.fullname, team.fullname))
                if team_choice not in team_choices:
                    team_choices.append(team_choice)
        self.fields['team'].queryset = teams
        self.fields['team'].widget = forms.Select(choices = EMPTY_SEL + team_choices)
        self.fields['budget_id'].choices = EMPTY_SEL + budget_choices
        
        NATURE_CHOICES = list(set(Budget.objects.filter(default_nature__isnull = False).values_list('default_nature',flat=True)))
        self.fields['nature'].choices = EMPTY_SEL + [(n,n) for n in NATURE_CHOICES]
