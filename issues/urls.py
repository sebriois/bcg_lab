from django.conf.urls.defaults import *

from issues.views import index, item, delete

urlpatterns = patterns('',
	url(r'^(?P<issue_id>\d+)/delete$', delete, name="issue_delete"),
	url(r'^(?P<issue_id>\d+)/$', item, name="issue_item"),
  url(r'^$', index, name="issue_index")
)
