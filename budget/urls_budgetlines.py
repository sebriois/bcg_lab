from django.conf.urls import *

from budget.views_budgetlines import index, item, delete, export_to_xls

urlpatterns = patterns('',
	url(r'^(?P<bl_id>\d+)/delete/$', delete, name="budgetline_delete"),
	url(r'^(?P<bl_id>\d+)/$', item, name="budgetline_item"),
	url(r'^export-to-xls/$', export_to_xls, name="budgetline_export"),
	url(r'^$', index, name="budgetlines")
)
