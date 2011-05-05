from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib import admin
from django.contrib.auth.views import login, logout_then_login

from home_view import home
from home_view import error

admin.autodiscover()

urlpatterns = patterns('',
    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/',        include(admin.site.urls)),
    (r'^products/',     include('product.urls')),
    (r'^providers/',    include('provider.urls')),
    (r'^orders/',       include('order.urls')),
    (r'^history/',      include('history.urls')),
    (r'^secretary/',    include('secretary.urls')),
    (r'^teams/',        include('team.urls_team')),
    (r'^members/',      include('team.urls_member')),
    (r'^login/$',       login, {'template_name': 'auth/login.html'}),
    url(r'^logout/$',   logout_then_login, name = "logout"),
    url(r'^error/$',    error, name="error"),
    url(r'^$',          home, name="home"),
)
