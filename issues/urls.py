from django.conf.urls.defaults import *

from issues.views import index

urlpatterns = patterns('',
  url(r'^$', index, name="issue_index")
)
