from django.conf.urls import *

from order.views_services import tab_services

urlpatterns = [
  path('$', tab_services, name="tab_services")
]