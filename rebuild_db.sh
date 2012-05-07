#! /bin/sh

dropdb order_manager
createdb order_manager -E utf8
python2.7 manage.py syncdb --no
export DJANGO_SETTINGS_MODULE=settings
python2.7 -c "print 'deleting content types...';from django.contrib.contenttypes.models import ContentType;ContentType.objects.all().delete();print 'delete done.'"
echo "Loading json data"
python2.7 manage.py loaddata saved_data.json
sudo apachectl restart