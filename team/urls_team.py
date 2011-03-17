from django.conf.urls.defaults import *

from team.views_team import index, item, new

urlpatterns = patterns('',
  url(r'^new/$', new, name="team_new"),
  url(r'^(?P<team_id>\d+)/$', item, name="team_item"),
  url(r'^$', index, name="team_index")
)
