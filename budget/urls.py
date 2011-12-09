from django.conf.urls.defaults import *

from budget.views import index, item, new
from budget.views import credit, debit, transfer, toggle

urlpatterns = patterns('',
  url(r'^create-budget/$', new, name="budget_new"),
  url(r'^transfer/$', transfer, name="budget_transfer"),

  url(r'^(?P<budget_id>\d+)/credit/$', credit, name="credit_budget"),
  url(r'^(?P<budget_id>\d+)/debit/$', debit, name="debit_budget"),
  url(r'^(?P<budget_id>\d+)/toggle/$', toggle, name="toggle_budget"),
  url(r'^(?P<budget_id>\d+)/$', item, name="budget_edit"),

  url(r'^$', index, name="budgets")
)
