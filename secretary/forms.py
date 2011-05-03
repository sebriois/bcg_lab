# coding: utf-8
from django import forms

from secretary.models import Budget, BudgetLine

class BudgetForm(forms.ModelForm):
  class Meta:
    model = Budget
    exclude = ('amount',)

class DebitBudgetForm(forms.ModelForm):
  class Meta:
    model = BudgetLine
    exclude = ('credit', 'debit', 'amount_left')
    
  def __init__( self, budget, *args, **kwargs ):
    super( DebitBudgetForm, self ).__init__( *args, **kwargs )
    
    self.fields['name'].initial = budget.name
    self.fields['name'].widget.attrs.update({'disabled':'disabled'})
    self.fields['nature'].initial = budget.default_nature
    self.fields['budget_type'].initial = budget.budget_type
    self.fields['credit_type'].initial = budget.default_credit_type
    
class CreditBudgetForm(forms.ModelForm):
  class Meta:
    model = BudgetLine
    exclude = ('debit', 'amount_left', 'order_nb', 'offer', 'ref', 'quantity', 'product_price')
    
  def __init__( self, budget, *args, **kwargs ):
    super( CreditBudgetForm, self ).__init__( *args, **kwargs )
    
    self.fields['name'].initial = budget.name
    self.fields['name'].widget.attrs.update({'disabled':'disabled'})
    self.fields['nature'].initial = budget.default_nature
    self.fields['budget_type'].initial = budget.budget_type
    self.fields['credit_type'].initial = budget.default_credit_type
