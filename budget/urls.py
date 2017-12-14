from django.urls import path

from budget.views import index, item, new
from budget.views import credit, debit, transfer, toggle

app_name = 'budget'
urlpatterns = [
  path('create-budget/', new, name="budget_new"),
  path('transfer/', transfer, name="budget_transfer"),

  path('<int:budget_id>/credit/', credit, name="credit_budget"),
  path('<int:budget_id>/debit/', debit, name="debit_budget"),
  path('<int:budget_id>/toggle/', toggle, name="toggle_budget"),
  path('<int:budget_id>/', item, name="budget_edit"),

  path('', index, name="budgets")
]