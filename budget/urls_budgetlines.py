from django.conf.urls.defaults import *

from budget.views_budgetlines import index, item, delete

urlpatterns = patterns('',
	url(r'^(?P<bl_id>\d+)/delete/$', delete, name="budgetline_delete"),
	url(r'^(?P<bl_id>\d+)/$', item, name="budgetline_item"),
	url(r'^$', index, name="budgetlines")
)
