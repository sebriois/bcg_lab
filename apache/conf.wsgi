import os, sys

sys.path.append('/var/www')
sys.path.append('/var/www/lbcmcp-orders')

os.environ['DJANGO_SETTINGS_MODULE'] = 'order_manager.settings'

import django.core.handlers.wsgi

application = django.core.handlers.wsgi.WSGIHandler()
