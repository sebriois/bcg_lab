from django.urls import path

from history.views import history_orders, history_budgets, item
from history.views import export_budget_to_xls, export_orders_to_xls

app_name = "history"
urlpatterns = [
    path('orders/', history_orders, name="orders"),
    path('budgets/', history_budgets, name="budgets"),
    path('export-budget-to-xls/', export_budget_to_xls, name="budget_export"),
    path('export-orders-to-xls/', export_orders_to_xls, name="orders_export"),
    path('<int:item_id>/', item, name="detail"),
]