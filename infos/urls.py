from django.conf.urls.defaults import *

from infos.views import index, new, delete

urlpatterns = patterns('',
	url(r'^(?P<info_id>\d+)/delete$', delete, name="info_delete"),
  url(r'^add-info/$', new, name="info_new"),
  url(r'^$', index, name="info_index")
)
