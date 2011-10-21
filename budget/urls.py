from django.conf.urls.defaults import *

from budget.views import index_budget, item_budget, new_budget
from budget.views import index_budgetline, delete_budgetline, edit_budgetline
from budget.views import credit_budget, debit_budget
from budget.views import transfer_budget, toggle_budget
from budget.views import history_budgetline

urlpatterns = patterns('',
  url(r'^create-budget/$', new_budget, name="budget_new"),
  url(r'^transfer/$', transfer_budget, name="budget_transfer"),

  url(r'^(?P<budget_id>\d+)/credit/$', credit_budget, name="credit_budget"),
  url(r'^(?P<budget_id>\d+)/debit/$', debit_budget, name="debit_budget"),
  url(r'^(?P<budget_id>\d+)/toggle/$', toggle_budget, name="toggle_budget"),
  url(r'^(?P<budget_id>\d+)/$', item_budget, name="budget_edit"),

  url(r'^budgetlines/(?P<bl_id>\d+)/edit/$', edit_budgetline, name="budgetline_edit"),
  url(r'^budgetlines/(?P<bl_id>\d+)/delete/$', delete_budgetline, name="budgetline_delete"),
  url(r'^budgetlines/history$', history_budgetline, name="history_budgets"),
  url(r'^budgetlines/$', index_budgetline, name="budgetlines"),
  url(r'^$', index_budget, name="budgets")
)
