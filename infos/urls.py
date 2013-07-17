from django.conf.urls import *

from infos.views import index, new, delete, item

urlpatterns = patterns('',
	url(r'^(?P<info_id>\d+)/delete$', delete, name="info_delete"),
	url(r'^(?P<info_id>\d+)/$', item, name="info_item"),
  url(r'^add-info/$', new, name="info_new"),
  url(r'^$', index, name="info_index")
)
