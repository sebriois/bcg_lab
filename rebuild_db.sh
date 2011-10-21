function error_exit
{
	echo "$1" 1>&2
	exit 1
}

sudo /usr/sbin/apachectl stop
python manage.py validate || error_exit "Schema could not be validated. Aborting"
python manage.py dumpdata auth.user budget history infos issues order product provider team > initial_data.json || error_exit "Dumpdata failed. Aborting"
sudo git pull origin master
dropdb order_manager -U briois
createdb order_manager -U briois -E utf8
python manage.py syncdb --no
sudo /usr/sbin/apachectl start
