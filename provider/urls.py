from django.conf.urls.defaults import *

from provider.views import index, item, delete, new

urlpatterns = patterns('',
  url(r'^new/$', new, name="provider_new"),
  url(r'^(?P<provider_id>\d+)/delete/$', delete, name="provider_delete"),
  url(r'^(?P<provider_id>\d+)/$', item, name="provider_item"),
  url(r'^$', index, name="provider_index")
)
