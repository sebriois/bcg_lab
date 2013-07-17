from django.conf.urls import *

from team.views_member import item, delete
from team.views_member import new_user, new_member, set_password
from team.views_member import toggle_active

urlpatterns = patterns('',
	url(r'^new-user/$', new_user, name="new_user"),
	url(r'^new-member/$', new_member, name="new_member"),
	url(r'^(?P<user_id>\d+)/set_password/$', set_password, name="set_password"),
	url(r'^(?P<user_id>\d+)/toggle-active/$', toggle_active, name="user_toggle_active"),
	url(r'^(?P<user_id>\d+)/delete/$', delete, name="user_delete"),
	url(r'^(?P<member_id>\d+)/$', item, name="user_item")
)
