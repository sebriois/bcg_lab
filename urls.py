from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib import admin
from django.contrib.auth.views import login, logout_then_login

from home_view import home
from home_view import error
from home_view import send_message

admin.autodiscover()

urlpatterns = patterns('',
    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
		(r'^admin/',            include(admin.site.urls)),
		(r'^administration/',   include('admin.urls')),
		(r'^products/',         include('product.urls')),
		(r'^providers/',        include('provider.urls')),
		(r'^orders/',           include('order.urls')),
		(r'^services/',					include('order.urls_services')),
		(r'^history/',					include('history.urls')),
		(r'^budgets/',					include('budget.urls')),
		(r'^budget-lines/',			include('budget.urls_budgetlines')),
		(r'^teams/',            include('team.urls_team')),
		(r'^members/',          include('team.urls_member')),
		(r'^issues/',						include('issues.urls')),
		(r'^infos/',						include('infos.urls')),
		(r'^preferences/',			include('preferences.urls')),
		(r'^login/$',           login, {'template_name': 'auth/login.html'}),
		url(r'^logout/$',       logout_then_login, name = "logout"),
		url(r'^error/$',        error, name="error"),
		url(r'^send-message/$', send_message, name="send_message"),
		url(r'^$',              home, name="home"),
)
