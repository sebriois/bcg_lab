#! /bin/sh

# Pour executer ce script:
# cd /var/www/lbcmcp-orders
# ./rebuild.sh

# Apache - arret du serveur web
sudo apachectl stop

# POSTGRESQL:
# suppression de la base
dropdb order_manager

# creation de la base
createdb order_manager -E utf8

# PYTHON/DJANGO:
# synchronisation des models django avec la base
# (ie. creation des tables dans la base)
python2.7 manage.py syncdb --no

# suppression des contenttypes en prevision du chargement des donnees
export DJANGO_SETTINGS_MODULE=settings
python2.7 -c "print 'deleting content types...';from django.contrib.contenttypes.models import ContentType;ContentType.objects.all().delete();print 'delete done.'"

# chargement du json (donnees) dans la base
echo "Loading json data"
sudo cp /mnt/sauvegardes/lbcmcp_orders/saved_data.json /var/www/lbcmcp-orders
python2.7 manage.py loaddata saved_data.json

# Apache - demarrage du serveur web
sudo apachectl start