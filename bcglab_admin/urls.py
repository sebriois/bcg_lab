from django.urls import path

from bcglab_admin.views import group_index, group_new, group_item, group_delete
from bcglab_admin.views import maintenance
from bcglab_admin.export_xls import export_all_budgets
from bcglab_admin.export_xls import export_history_budgets
from bcglab_admin.export_xls import export_history_orders
from bcglab_admin.export_xls import export_all_products

app_name = 'bcglab_admin'
urlpatterns = [
    path('groups/<int:group_id>/delete$', group_delete, name="group_delete"),
    path('groups/<int:group_id>/$', group_item, name="group_item"),
    path('groups/new/$', group_new, name="group_new"),
    path('groups/$', group_index, name="group_index"),
    path('maintenance/$', maintenance, name="maintenance"),
    path('export_all_budgets/$', export_all_budgets, name="export_all_budgets"),
    path('export_history_budgets/$', export_history_budgets, name="export_history_budgets"),
    path('export_history_orders/$', export_history_orders, name="export_history_orders"),
    path('export_all_products/$', export_all_products, name="export_all_products")
]