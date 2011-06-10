import os
import sys

project_name = os.path.basename(os.path.abspath( os.path.dirname(__file__) + "/../"))
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../', '../'))

sys.path.append(root_path)
sys.path.append("%s/%s" % (root_path,project_name))

os.environ['DJANGO_SETTINGS_MODULE'] = '%s.settings' % project_name

import django.core.handlers.wsgi

application = django.core.handlers.wsgi.WSGIHandler()