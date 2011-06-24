from django.conf.urls.defaults import *

from issues.views import index, item, delete, set_status

urlpatterns = patterns('',
	url(r'^(?P<issue_id>\d+)/delete$', delete, name="issue_delete"),
	url(r'^(?P<issue_id>\d+)/status/(?P<status>\d+)$', set_status, name="issue_status"),
	url(r'^(?P<issue_id>\d+)/$', item, name="issue_item"),
  url(r'^$', index, name="issue_index")
)
