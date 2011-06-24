from django.conf.urls.defaults import *

from infos.views import index

urlpatterns = patterns('',
  url(r'^$', index, name="infos")
)
