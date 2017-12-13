from django.conf.urls import *

from team.views_member import item, delete
from team.views_member import new_user, new_member, set_password
from team.views_member import toggle_active

urlpatterns = [
    path('new-user/$', new_user, name="new_user"),
    path('new-member/$', new_member, name="new_member"),
    path('<int:user_id>/set_password/$', set_password, name="set_password"),
    path('<int:user_id>/toggle-active/$', toggle_active, name="user_toggle_active"),
    path('<int:user_id>/delete/$', delete, name="user_delete"),
    path('<int:member_id>/$', item, name="user_item")
]