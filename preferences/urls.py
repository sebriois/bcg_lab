from django.urls import path

from preferences.views import index, change_password

app_name = "preferences"
urlpatterns = [
    path('change_password/', change_password, name = "change_password"),
    path('', index, name = "preferences")
]
