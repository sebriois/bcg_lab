from django.conf.urls.defaults import *

from infos.views import index, delete

urlpatterns = patterns('',
	url(r'^(?P<info_id>\d+)/delete$', delete, name="info_delete"),
  url(r'^$', index, name="info_index")
)
