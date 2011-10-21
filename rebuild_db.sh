sudo /usr/sbin/apachectl stop
python manage.py dumpdata --indent=2 > initial_data.json
dropdb order_manager -U briois
createdb order_manager -U briois -E utf8
python manage.py syncdb --no
sudo /usr/sbin/apachectl start
