from django.conf.urls.defaults import *

from budget.views import index_budget, item_budget, new_budget
from budget.views import index_budgetline
from budget.views import credit_budget, debit_budget

urlpatterns = patterns('',
  url(r'^create-budget/$', new_budget, name="budget_new"),
  url(r'^(?P<budget_id>\d+)/credit/$', credit_budget, name="credit_budget"),
  url(r'^(?P<budget_id>\d+)/debit/$', debit_budget, name="debit_budget"),
  url(r'^budgetlines/$', index_budgetline, name="budgetlines"),
  url(r'^(?P<budget_id>\d+)/$', item_budget, name="budget_edit"),
  url(r'^$', index_budget, name="budgets")
)
