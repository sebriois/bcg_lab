from django.conf.urls.defaults import *

from history.views import index, item

urlpatterns = patterns('',
  url(r'^(?P<item_id>\d+)/$', item, name="history_detail"),
  url(r'^$', index, name="history")
)
