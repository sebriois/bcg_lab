from django.urls import path

from order.views_services import tab_services

app_name = 'services'
urlpatterns = [
  path('$', tab_services, name="tab_services")
]