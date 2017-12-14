from django.urls import path

from attachments.views import new, delete

app_name = "attachments"
urlpatterns = [
    path('<int:attachment_id>/delete/', delete, name="delete"),
    path('new/', new, name="new")
]
