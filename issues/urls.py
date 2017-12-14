from django.urls import path

from issues.views import index, item, delete, set_status, new

app_name = "issues"
urlpatterns = [
    path('<int:issue_id>/delete', delete, name="issue_delete"),
    path('<int:issue_id>/status/<int:status>', set_status, name="issue_status"),
    path('<int:issue_id>/', item, name="issue_item"),
    path('new', new, name="issue_new"),
    path('', index, name="issue_index")
]