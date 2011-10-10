# coding: utf-8
from django import forms

from budget.models import Budget, BudgetLine

class BudgetForm(forms.ModelForm):
	class Meta:
		model = Budget
		exclude = ('is_active',)
	
class BudgetLineForm(forms.ModelForm):
	class Meta:
		model = BudgetLine
		exclude = ('order_id', 'orderitem_id', 'budget_id', 'credit', 'debit', 'product_price')
	
	def __init__( self, *args, **kwargs ):
		super( BudgetLineForm, self ).__init__( *args, **kwargs )
		
		if self.instance and self.instance.credit:
			initial_cost = self.instance.credit
		elif self.instance and self.instance.debit:
			initial_cost = self.instance.debit
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
