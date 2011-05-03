dropdb order_manager -U briois
createdb order_manager -U briois -E utf8
python manage.py syncdb --no
#python load_db.py
sudo /usr/sbin/apachectl restart
