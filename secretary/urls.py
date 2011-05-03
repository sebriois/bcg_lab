from django.conf.urls.defaults import *

from secretary.views import orders, index_budget, new_budget
from secretary.views import credit_budget, debit_budget, reports

urlpatterns = patterns('',
  url(r'^create-budget/$', new_budget, name="budget_new"),
  url(r'^(?P<budget_id>\d+)/credit/$', credit_budget, name="credit_budget"),
  url(r'^(?P<budget_id>\d+)/debit/$', debit_budget, name="debit_budget"),
  url(r'^budgets/$', index_budget, name="secretary_budgets"),
  url(r'^reports/$', reports, name="secretary_reports"),
  url(r'^$', orders, name="secretary_orders"),
)
