from django.conf.urls import *

from team.views_team import index, item, new, add_user_to_team

urlpatterns = patterns('',
	url(r'^(?P<team_id>\d+)/$', item, name="team_item"),
  url(r'^add-user/(?P<user_id>\d+)/$', add_user_to_team, name="add_user_to_team"),
  url(r'^new/$', new, name="team_new"),
  url(r'^$', index, name="team_index")
)
