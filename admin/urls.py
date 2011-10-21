from django.conf.urls.defaults import *

from admin.views import group_index, group_new, group_item
from admin.views import perm_index

urlpatterns = patterns('',
	url(r'^groups/(?P<group_id>\d+)/$', group_item, name="group_item"),
  url(r'^groups/new/$', group_new, name="group_new"),
  url(r'^groups/$', group_index, name="group_index"),
  url(r'^permissions/$', perm_index, name="perm_index")
)
