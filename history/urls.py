from django.conf.urls import *

from history.views import history_orders, history_budgets, item
from history.views import export_budget_to_xls, export_orders_to_xls

urlpatterns = patterns('',
  url(r'^orders/$', history_orders, name="history_orders"),
  url(r'^budgets/$', history_budgets, name="history_budgets"),
  url(r'^export-budget-to-xls/$', export_budget_to_xls, name="history_budget_export"),
  url(r'^export-orders-to-xls/$', export_orders_to_xls, name="history_orders_export"),
  url(r'^(?P<item_id>\d+)/$', item, name="history_detail"),
)
