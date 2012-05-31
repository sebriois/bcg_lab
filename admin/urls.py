from django.conf.urls.defaults import *

from admin.views import group_index, group_new, group_item, group_delete
from admin.views import maintenance

urlpatterns = patterns('',
	url(r'^groups/(?P<group_id>\d+)/delete$', group_delete, name="group_delete"),
	url(r'^groups/(?P<group_id>\d+)/$', group_item, name="group_item"),
	url(r'^groups/new/$', group_new, name="group_new"),
	url(r'^groups/$', group_index, name="group_index"),
	url(r'^maintenance/$', maintenance, name="maintenance")
)
