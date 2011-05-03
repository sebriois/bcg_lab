import os
import sys

path = '/home/briois/srv/www'
if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'order_manager.settings'

import django.core.handlers.wsgi

application = django.core.handlers.wsgi.WSGIHandler()
