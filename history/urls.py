from django.urls import path

from history.views import history_orders, history_budgets, item
from history.views import export_budget_to_xls, export_orders_to_xls

urlpatterns = [
    path('orders/$', history_orders, name="history_orders"),
    path('budgets/$', history_budgets, name="history_budgets"),
    path('export-budget-to-xls/$', export_budget_to_xls, name="history_budget_export"),
    path('export-orders-to-xls/$', export_orders_to_xls, name="history_orders_export"),
    path('<int:item_id>/$', item, name="history_detail"),
]