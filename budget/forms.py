# coding: utf-8
from django import forms

from budget.models import Budget, BudgetLine

class BudgetForm(forms.ModelForm):
  class Meta:
    model = Budget
  


class DebitBudgetForm(forms.ModelForm):
  class Meta:
    model = BudgetLine
    exclude = ('credit', 'debit')
  
  def __init__( self, budget, *args, **kwargs ):
    super( DebitBudgetForm, self ).__init__( *args, **kwargs )
    
    self.fields['name'].initial = budget.name
    self.fields['name'].widget.attrs.update({'disabled':'disabled'})
    self.fields['nature'].initial = budget.default_nature
    self.fields['budget_type'].initial = budget.budget_type
    self.fields['credit_type'].initial = budget.default_credit_type
    self.fields['date'] = forms.DateField( 
      label         = "Date de l'acte",
      input_formats = ["%d/%m/%Y"],
      widget        = forms.TextInput( attrs = { 'class' : 'datepicker' }),
      required      = False
    )
  


class CreditBudgetForm(forms.ModelForm):
  class Meta:
    model = BudgetLine
    exclude = ('debit', 'number', 'offer', 'ref', 'quantity', 'product_price')
  
  def __init__( self, budget, *args, **kwargs ):
    super( CreditBudgetForm, self ).__init__( *args, **kwargs )
    
    self.fields['team'].initial = budget.team.name
    self.fields['team'].widget.attrs.update({'disabled':'disabled'})
    self.fields['name'].initial = budget.name
    self.fields['name'].widget.attrs.update({'disabled':'disabled'})
    self.fields['nature'].initial = budget.default_nature
    self.fields['budget_type'].initial = budget.budget_type
    self.fields['credit_type'].initial = budget.default_credit_type
    # self.fields['credit'].required = True ????
    self.fields['date'] = forms.DateField( 
      label         = "Date de l'acte",
      input_formats = ["%d/%m/%Y"],
      widget        = forms.TextInput( attrs = { 'class' : 'datepicker' }),
      required      = False
    )
  
