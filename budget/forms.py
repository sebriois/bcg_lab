# coding: utf-8
from django import forms

from budget.models import Budget, BudgetLine

class BudgetForm(forms.ModelForm):
	class Meta:
		model = Budget
		exclude = ('is_active',)
	


class DebitBudgetForm(forms.ModelForm):
	class Meta:
		model = BudgetLine
		fields = ('budget', 'product', 'product_price')
	
	def __init__( self, budget, *args, **kwargs ):
		super( DebitBudgetForm, self ).__init__( *args, **kwargs )
		
		self.fields['budget'].initial = budget.name
		self.fields['budget'].widget.attrs.update({'disabled':'disabled'})
		self.fields['product'].required = True
		self.fields['product_price'].required = True
	

class CreditBudgetForm(forms.ModelForm):
	class Meta:
		model = BudgetLine
		fields = ('budget', 'product', 'product_price')
	
	def __init__( self, budget, *args, **kwargs ):
		super( CreditBudgetForm, self ).__init__( *args, **kwargs )
		
		self.fields['budget'].initial = budget.name
		self.fields['budget'].widget.attrs.update({'disabled':'disabled'})
		self.fields['product'].required = True
		self.fields['product_price'].required = True
	

