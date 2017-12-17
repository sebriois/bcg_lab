from django.urls import path

from issues.views import index, item, delete, set_status, new

app_name = "issues"
urlpatterns = [
    path('<int:issue_id>/delete', delete, name = "delete"),
    path('<int:issue_id>/status/<int:status>', set_status, name = "status"),
    path('<int:issue_id>/', item, name = "item"),
    path('new', new, name = "new"),
    path('', index, name = "index")
]
