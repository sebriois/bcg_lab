from django.conf.urls import *

from bcglab_admin.views import group_index, group_new, group_item, group_delete
from bcglab_admin.views import maintenance
from bcglab_admin.export_xls import export_all_budgets
from bcglab_admin.export_xls import export_history_budgets
from bcglab_admin.export_xls import export_history_orders
from bcglab_admin.export_xls import export_all_products

urlpatterns = [
    url(r'^groups/(?P<group_id>\d+)/delete$', group_delete, name="group_delete"),
    url(r'^groups/(?P<group_id>\d+)/$', group_item, name="group_item"),
    url(r'^groups/new/$', group_new, name="group_new"),
    url(r'^groups/$', group_index, name="group_index"),
    url(r'^maintenance/$', maintenance, name="maintenance"),
    url(r'^export_all_budgets/$', export_all_budgets, name="export_all_budgets"),
    url(r'^export_history_budgets/$', export_history_budgets, name="export_history_budgets"),
    url(r'^export_history_orders/$', export_history_orders, name="export_history_orders"),
    url(r'^export_all_products/$', export_all_products, name="export_all_products")
]