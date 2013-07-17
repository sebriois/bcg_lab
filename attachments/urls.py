from django.conf.urls import *

from attachments.views import new, delete

urlpatterns = patterns('',
	url(r'^(?P<attachment_id>\d+)/delete/$', delete, name="attachment_delete"),
  url(r'^new/$', new, name="attachment_new")
)
