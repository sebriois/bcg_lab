from django.conf.urls import *

from attachments.views import new, delete

urlpatterns = [
    url(r'^(?P<attachment_id>\d+)/delete/$', delete, name="delete"),
    url(r'^new/$', new, name="new")
]
