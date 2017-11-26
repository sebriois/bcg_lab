from django.conf.urls import *
from django.conf import settings
from django.contrib import admin
from django.contrib.auth.views import login, logout_then_login

from bcg_lab.home_view import error, send_message, home

admin.autodiscover()

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    # url(r'^static/(.*)', 'django.views.static.serve', {'show_indexes': settings.DEBUG }),
    # url(r'^media/(.*)', 'django.views.static.serve', {'document_root' : settings.MEDIA_ROOT, 'show_indexes': settings.DEBUG }),
    url(r'^attachments/', include('attachments.urls', namespace = 'attachments', app_name = 'attachments')),
    url(r'^administration/', include('bcglab_admin.urls')),
    url(r'^products/', include('product.urls')),
    url(r'^product-codes/', include('product.urls_productcode')),
    url(r'^providers/', include('provider.urls')),
    url(r'^orders/', include('order.urls')),
    url(r'^services/', include('order.urls_services')),
    url(r'^history/', include('history.urls')),
    url(r'^budgets/', include('budget.urls')),
    url(r'^budget-lines/', include('budget.urls_budgetlines')),
    url(r'^teams/', include('team.urls_team')),
    url(r'^members/', include('team.urls_member')),
    url(r'^issues/', include('issues.urls')),
    url(r'^infos/', include('infos.urls')),
    url(r'^preferences/', include('preferences.urls')),
    url(r'^login/$', login, {'template_name': 'auth/login.html'}, name = 'login'),
    url(r'^logout/$', logout_then_login, name = "logout"),
    url(r'^error/$', error, name="error"),
    url(r'^send-message/$', send_message, name="send_message"),
    url(r'^$', home, name="home"),
]
