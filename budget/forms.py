# coding: utf-8
from django import forms

from budget.models import Budget, BudgetLine
from team.models import Team
from provider.models import Provider
from product.models import Product
from utils import *
from constants import *

class BudgetForm(forms.ModelForm):
	all_natures = forms.DecimalField(
		label = u"Toute nature",
		help_text = u"(Pas d'attribution par nature)",
		min_value = 0,
		required = False
	)
	fo = forms.DecimalField(
		label = u"FO",
		min_value = 0,
		required = False
	)
	mi = forms.DecimalField(
		label = u"MI",
		min_value = 0,
		required = False
	)
	sa = forms.DecimalField(
		label = u"SA",
		min_value = 0,
		required = False
	)
	eq = forms.DecimalField(
		label = u"EQ",
		min_value = 0,
		required = False
	)
	
	class Meta:
		model = Budget
		exclude = ('is_active','default_nature')


class BudgetLineForm(forms.ModelForm):
	budget = forms.ModelChoiceField( 
		label = u"Budget",
		queryset = Budget.objects.filter(is_active=True),
		required = True
	)
	
	class Meta:
		model = BudgetLine
		fields = ('provider','number','budget_id','offer','product','reference','quantity')
	
	def __init__( self, *args, **kwargs ):
		super( BudgetLineForm, self ).__init__( *args, **kwargs )
		initial_cost = 0
		
		if self.instance:
			if self.instance.credit:
				initial_cost = self.instance.credit
			elif self.instance.debit:
				initial_cost = self.instance.debit
			self.fields['budget'].initial = Budget.objects.get(id = self.instance.budget_id)
		
		self.fields["cost"] = forms.DecimalField(
			label = u"Montant unitaire",
			initial = initial_cost
		)
		self.fields["quantity"].required = True
		
	

class DebitBudgetForm(forms.ModelForm):
	class Meta:
		model = BudgetLine
		fields = ('budget', 'number', 'product', 'product_price')
	
	def __init__( self, budget, *args, **kwargs ):
		super( DebitBudgetForm, self ).__init__( *args, **kwargs )
		
		self.fields['budget'].initial = budget.name
		self.fields['budget'].widget.attrs.update({'disabled':'disabled'})
		self.fields['product'].required = True
		self.fields['product_price'].required = True
	

class CreditBudgetForm(forms.ModelForm):
	class Meta:
		model = BudgetLine
		fields = ('budget', 'number', 'product', 'product_price')
	
	def __init__( self, budget, *args, **kwargs ):
		super( CreditBudgetForm, self ).__init__( *args, **kwargs )
		
		self.fields['budget'].initial = budget.name
		self.fields['budget'].widget.attrs.update({'disabled':'disabled'})
		self.fields['product'].required = True
		self.fields['product_price'].required = True
	

class TransferForm(forms.Form):
	title1 = forms.CharField( label = u"Désignation", max_length = 100, required = False )
	title2 = forms.CharField( label = u"Désignation", max_length = 100, required = False )
	budget1 = forms.ModelChoiceField( label = u"Débiter", queryset = Budget.objects.filter(is_active = True) )
	budget2 = forms.ModelChoiceField( label = u"Créditer", queryset = Budget.objects.filter(is_active = True) )
	amount = forms.DecimalField( label = u"Montant" )


class BudgetLineFilterForm(forms.Form):
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
	
	budget_type = forms.ChoiceField(
		label = "Tutelle",
		choices = EMPTY_SEL + [(0, u"CNRS"),(1, u"UPS")],
		required = False
	)
	
	budget_id = forms.ChoiceField(
		label			= "Budget",
		choices		= EMPTY_SEL,
		required	= False
	)
	
	nature = forms.ChoiceField(
		label			= "Nature",
		choices		= EMPTY_SEL,
		required	= False
	)
	
	number = forms.CharField(
		label			= "N°cmde",
		required	= False
	)
	
	product = forms.CharField(
		label			= u"Produit",
		help_text	= "Appuyez sur 'esc' pour fermer la liste de choix.",
		required 	= False
	)
	
	provider = forms.ChoiceField(
		label			= "Fournisseur",
		choices		= EMPTY_SEL,
		required	= False
	)
	
	origin = forms.CharField(
		label			= "Origine (Code)",
		required	= False
	)
	
	date__gte = forms.DateField( 
		label					= "Date d'enregistrement min",
		input_formats = ["%d/%m/%Y"],
		widget				= forms.TextInput( attrs = { 'class' : 'datepicker maxToday' }),
		required			= False
	)
	
	date__lte = forms.DateField( 
		label					= "Date d'enregistrement max",
		input_formats = ["%d/%m/%Y"],
		widget				= forms.TextInput( attrs = { 'class' : 'datepicker maxToday' }),
		required			= False
	)
	
	def __init__(self, user, *args, **kwargs):
		super( BudgetLineFilterForm, self ).__init__(*args, **kwargs)
		
		if user.has_perm('team.custom_view_teams'):
			teams = [t.name for t in Team.objects.all()]
			budget_choices = [(b.id,b.name) for b in Budget.objects.filter(is_active=True)]
		else:
			teams = [t.name for t in get_teams(user)]
			budget_choices = [(b.id,b.name) for b in Budget.objects.filter(is_active=True, team__in=get_teams(user))]
		
		name_choices = []
		number_choices = []
		for bl in BudgetLine.objects.filter(is_active = True, team__in = teams):
			if bl.product and not bl.product in name_choices:
				name_choices.append(bl.product)
			if bl.number and not bl.number in number_choices:
				number_choices.append(bl.number)
		
		self.fields['budget_id'].choices = EMPTY_SEL + budget_choices
		self.fields['team'].choices = EMPTY_SEL + [(name,name) for name in teams]
		self.fields['product'].widget = forms.TextInput( attrs = {
			'class' : 'autocomplete',
			'choices': ";".join(name_choices)
		})
		self.fields['number'].widget = forms.TextInput( attrs = {
			'class' : 'autocomplete',
			'choices': ";".join(number_choices)
		})
		self.fields['provider'].choices = EMPTY_SEL + [(p.name, p.name) for p in Provider.objects.exclude(is_service = True)]
		NATURE_CHOICES = list(set(Budget.objects.filter(default_nature__isnull = False).values_list('default_nature',flat=True)))
		self.fields['nature'].choices = EMPTY_SEL + [(n,n) for n in NATURE_CHOICES]


