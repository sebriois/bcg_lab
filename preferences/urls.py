from django.conf.urls import *

from preferences.views import index, change_password

urlpatterns = [
	path('change_password/$', change_password, name="change_password"),
	path('$', index, name="preferences")
]