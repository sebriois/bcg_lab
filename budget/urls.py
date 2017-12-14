from django.urls import path

from budget.views import index, item, new
from budget.views import credit, debit, transfer, toggle

app_name = 'budget'
urlpatterns = [
  path('create-budget/', new, name="new"),
  path('transfer/', transfer, name="transfer"),

  path('<int:budget_id>/credit/', credit, name="credit"),
  path('<int:budget_id>/debit/', debit, name="debit"),
  path('<int:budget_id>/toggle/', toggle, name="toggle"),
  path('<int:budget_id>/', item, name="edit"),

  path('', index, name="list")
]