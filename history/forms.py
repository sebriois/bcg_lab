# coding: utf-8
from django import forms

from team.models import Team
from provider.models import Provider
from product.models import Product
from history.models import History
from budget.models import Budget, BudgetLine
from order.models import OrderItem
from utils import *
from bcg_lab.constants import *

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
        label       = u"Produit",
        required    = False
    )
    items__reference = forms.CharField(
        label     = u"Référence",
        help_text = "Appuyez sur 'esc' pour fermer la liste de choix.",
        required  = False
    )
    items__origin = forms.CharField(
        label     = u"Fournisseur d'origine",
        help_text = "Appuyez sur 'esc' pour fermer la liste de choix.",
        required  = False
    )
    items__category = forms.ChoiceField(
        label       = "Type",
        choices = EMPTY_SEL,
        required = False
    )
    items__sub_category = forms.ChoiceField(
        label       = "Sous-type",
        choices = EMPTY_SEL,
        required = False
    )
    provider = forms.ModelChoiceField( 
        label    = u"Fournisseur",
        queryset = Provider.objects.exclude(is_service = True),
        required = False
    )
    number = forms.CharField(
        label = u"N° de commande",
        required = False
    )
    date_delivered__gte = forms.DateField( 
        label         = "Date d'enregistrement min",
        input_formats = ["%d/%m/%Y"],
        widget        = forms.TextInput( attrs = { 'class' : 'datepicker maxToday' }),
        required      = False
    )
    date_delivered__lte = forms.DateField( 
        label         = "Date d'enregistrement max",
        input_formats = ["%d/%m/%Y"],
        widget        = forms.TextInput( attrs = { 'class' : 'datepicker maxToday' }),
        required      = False
    )
    
    def __init__(self, user, *args, **kwargs):
        super( HistoryFilterForm, self ).__init__(*args, **kwargs)
        
        if user.has_perm('team.custom_view_teams'):
            teams = Team.objects.all()
            history = History.objects.filter( team__in = [t.name for t in teams] )
        elif user.has_perm("order.custom_view_local_provider"):
            teams = Team.objects.all()
            history = History.objects.filter( provider__iexact = "magasin" )
        else:
            teams = get_teams(user)
            history = History.objects.filter( team__in = [t.name for t in teams] )
        
        ref_choices = []
        origin_choices = []
        for h in history:
            for i in h.items.all():
                if i.reference and not i.reference in ref_choices:
                    ref_choices.append(i.reference)
                if i.origin and i.origin != '' and not i.origin in origin_choices:
                    origin_choices.append( i.origin )
        
        self.fields['team'].queryset = teams
        self.fields['items__reference'].widget = forms.TextInput( attrs={
            'class' : 'autocomplete',
            'choices': ";".join(ref_choices)
        })
        self.fields['items__origin'].widget = forms.TextInput( attrs={
            'class' : 'autocomplete',
            'choices': ";".join(origin_choices)
        })
        
        categories = list(set(OrderItem.objects.values_list('category', flat = True).order_by('category')))
        sub_categories = list(set(OrderItem.objects.values_list('sub_category', flat = True).order_by('sub_category')))
        self.fields['items__category'].choices = EMPTY_SEL + [(c,c) for c in categories]
        self.fields['items__sub_category'].choices = EMPTY_SEL + [(sc, sc) for sc in sub_categories]
    

class BudgetHistoryFilterForm(forms.Form):
    connector = forms.TypedChoiceField(
        choices = [("OR", u"l'une des"), ("AND",u"toutes les")],
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
        label           = "Budget",
        choices     = EMPTY_SEL,
        required    = False
    )
    nature = forms.ChoiceField(
        label           = "Nature",
        choices     = EMPTY_SEL,
        required    = False
    )
    number = forms.CharField(
        label           = "N°cmde",
        required    = False
    )
    product__icontains = forms.CharField(
        label       = u"Produit",
        required    = False
    )
    provider = forms.ModelChoiceField(
        label    = "Fournisseur",
        queryset = Provider.objects.exclude(is_service = True),
        required = False
    )
    date__gte = forms.DateField( 
        label         = "Date d'enregistrement min",
        input_formats = ["%d/%m/%Y"],
        widget        = forms.TextInput( attrs = { 'class' : 'datepicker maxToday' }),
        required      = False
    )
    date__lte = forms.DateField( 
        label         = "Date d'enregistrement max",
        input_formats = ["%d/%m/%Y"],
        widget        = forms.TextInput( attrs = { 'class' : 'datepicker maxToday' }),
        required      = False
    )
    
    def __init__(self, user, *args, **kwargs):
        super( BudgetHistoryFilterForm, self ).__init__(*args, **kwargs)
        
        if user.has_perm('team.custom_view_teams'):
            teams = Team.objects.all()
            budget_choices = [(b.id,b.name) for b in Budget.objects.filter(is_active=False)]
        else:
            teams = get_teams(user)
            budget_choices = [(b.id,b.name) for b in Budget.objects.filter(is_active=False, team__in = [t.name for t in teams])]
        
        name_choices = []
        number_choices = []
        for bl in BudgetLine.objects.filter(is_active = False, team__in = [t.name for t in teams]):
            if bl.number and not bl.number in number_choices:
                number_choices.append(bl.number)
        
        self.fields['team'].queryset = teams
        self.fields['budget_id'].choices = EMPTY_SEL + budget_choices
        self.fields['number'].widget = forms.TextInput( attrs = {
            'class' : 'autocomplete',
            'choices': ";".join(number_choices)
        })
        NATURE_CHOICES = list(set(Budget.objects.filter(default_nature__isnull = False).values_list('default_nature',flat=True)))
        self.fields['nature'].choices = EMPTY_SEL + [(n,n) for n in NATURE_CHOICES]
    
