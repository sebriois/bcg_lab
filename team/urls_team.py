from django.urls import path

from team.views_team import index, item, new, add_user_to_team

app_name = "team"
urlpatterns = [
    path('<int:team_id>/', item, name = "item"),
    path('add-user/<int:user_id>/', add_user_to_team, name = "add_user"),
    path('new/', new, name = "new"),
    path('', index, name = "index")
]
