from django.conf.urls.defaults import *

from order.views_services import tab_services

urlpatterns = patterns('',
  url(r'^$', tab_services, name="tab_services")
)
