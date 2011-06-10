import os
import sys

root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../', '../'))

sys.path.append(root_path)
sys.path.append("%s/lbcmcp-orders" % root_path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'lbcmcp-orders.settings'

import django.core.handlers.wsgi

application = django.core.handlers.wsgi.WSGIHandler()