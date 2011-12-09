# coding: utf-8
from django import forms

from budget.models import Budget, BudgetLine
from team.models import Team
from provider.models import Provider
from product.models import Product

class BudgetForm(forms.ModelForm):
	class Meta:
		model = Budget
		exclude = ('is_active',)
	
class BudgetLineForm(forms.ModelForm):
	budget = forms.ModelChoiceField(
		label = u"Budget",
		queryset = Budget.objects.filter(is_active = True),
		required = True
	)
	
	class Meta:
		model = BudgetLine
		fields = ('provider','number','offer','product','reference','quantity')
	
	def __init__( self, *args, **kwargs ):
		super( BudgetLineForm, self ).__init__( *args, **kwargs )
		
		if self.instance:
			if self.instance.credit:
				initial_cost = self.instance.credit
			elif self.instance.debit:
				initial_cost = self.instance.debit
			self.fields['budget'].initial = Budget.objects.get(name = self.instance.budget)
		else:
			initial_cost = 0
		
		self.fields["cost"] = forms.DecimalField( label = u"Montant unitaire", initial = initial_cost)
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
	budget1 = forms.ModelChoiceField( label = u"Débiter", queryset = Budget.objects.filter(is_active = True) )
	budget2 = forms.ModelChoiceField( label = u"Créditer", queryset = Budget.objects.filter(is_active = True) )
	amount = forms.DecimalField( label = u"Montant" )


class BudgetLineFilterForm(forms.Form):
	TEAM_CHOICES = [(team.name,team.name) for team in Team.objects.all()]
	PROVIDER_CHOICES = [(p.name, p.name) for p in Provider.objects.exclude(is_service = True)]
	ORIGIN_CHOICES = ";".join( set([ unicode(p.origin) for p in Product.objects.all() ]) )
	PRODUCT_CHOICES = ";".join( [ unicode(p) for p in Product.objects.all() ] )
	REFERENCE_CHOICES = ";".join( [ unicode(p.reference) for p in Product.objects.all() ] )
	
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

	items__name = forms.CharField(
		label			= u"Produit",
		widget		= forms.TextInput( attrs = {
			'class' : 'autocomplete',
			'choices': PRODUCT_CHOICES
		}),
		help_text	= "Appuyez sur 'esc' pour fermer la liste de choix.",
		required 	= False
	)
	
	items__reference = forms.CharField(
		label			= u"Référence",
		widget		= forms.TextInput( attrs = {
			'class' : 'autocomplete',
			'choices': REFERENCE_CHOICES
		}),
		help_text = "Appuyez sur 'esc' pour fermer la liste de choix.",
		required 	= False
	)
	
	provider = forms.ChoiceField(
		label			= "Fournisseur",
		choices		= [("","---------")] + PROVIDER_CHOICES,
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
		super( BudgetLineFilterForm, self ).__init__(*args, **kwargs)
		
		if user.has_perm('team.view_all_teams'):
			team_choices = [("","---------")] + [(team.name,team.name) for team in Team.objects.all()]
		else:
			team_choices = [("","---------")] + [(team.name,team.name) for team in get_teams(user)]
		
		self.fields['team'].choices = team_choices
		# TODO:
		# self.fields['team'].initial = get_teams(user)[0].name
	

	
