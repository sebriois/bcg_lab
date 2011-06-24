from django.conf.urls.defaults import *

from infos.views import index, item

urlpatterns = patterns('',
  url(r'^(?P<item_id>\d+)/$', item, name="info_detail"),
  url(r'^$', index, name="infos")
)
