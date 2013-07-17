from django.conf.urls import *

from preferences.views import index, change_password

urlpatterns = patterns('',
	url(r'^change_password/$', change_password, name="change_password"),
	url(r'^$', index, name="preferences")
)
