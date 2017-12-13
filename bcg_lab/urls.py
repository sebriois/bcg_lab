from django.conf.urls import *
from django.contrib import admin
from django.contrib.auth.views import login, logout_then_login
from django.urls import path

from bcg_lab.home_view import error, send_message, home

admin.autodiscover()

urlpatterns = [
    path("admin/", admin.site.urls),
    # path('static/(.*)', 'django.views.static.serve', {'show_indexes': settings.DEBUG }),
    # path('media/(.*)', 'django.views.static.serve', {'document_root' : settings.MEDIA_ROOT, 'show_indexes': settings.DEBUG }),
    path('attachments/', include('attachments.urls', namespace = 'attachments')),
    path('administration/', include('bcglab_admin.urls', namespace = 'bcglab_admin')),
    path('products/', include('product.urls', namespace = 'product')),
    path('product-codes/', include('product.urls_productcode', namespace = 'product_code')),
    path('providers/', include('provider.urls', namespace = 'provider')),
    path('orders/', include('order.urls', namespace = 'order')),
    path('services/', include('order.urls_services', namespace = 'services')),
    path('history/', include('history.urls', namespace = 'history')),
    path('budgets/', include('budget.urls', namespace = 'budget')),
    path('budget-lines/', include('budget.urls_budgetlines', namespace = 'budget_line')),
    path('teams/', include('team.urls_team', namespace = 'team')),
    path('members/', include('team.urls_member', namespace = 'team_member')),
    path('issues/', include('issues.urls', namespace = 'issues')),
    path('infos/', include('infos.urls', namespace = 'infos')),
    path('preferences/', include('preferences.urls', namespace = 'preferences')),
    path('login/$', login, {'template_name': 'auth/login.html'}, name = 'login'),
    path('logout/$', logout_then_login, name = "logout"),
    path('error/$', error, name="error"),
    path('send-message/$', send_message, name="send_message"),
    path('$', home, name="home"),
]
