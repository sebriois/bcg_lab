from django.conf.urls.defaults import *

from history.views import history_orders, history_budgets, item

urlpatterns = patterns('',
  url(r'^orders/$', history_orders, name="history_orders"),
  url(r'^budgets/$', history_budgets, name="history_budgets"),
  url(r'^(?P<item_id>\d+)/$', item, name="history_detail"),
)
