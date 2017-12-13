from django.urls import path

from team.views_team import index, item, new, add_user_to_team

urlpatterns = [
    path('<int:team_id>/$', item, name="team_item"),
    path('add-user/<int:user_id>/$', add_user_to_team, name="add_user_to_team"),
    path('new/$', new, name="team_new"),
    path('$', index, name="team_index")
]