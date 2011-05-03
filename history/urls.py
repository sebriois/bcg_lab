from django.conf.urls.defaults import *

from history.views import index

urlpatterns = patterns('',
  url(r'^$', index, name="history")
)
