./manage.py syncdb
./manage.py migrate --no-initial-data
./manage.py loaddata fixtures/initial.json
./manage.py reset_domain
./manage.py collectstatic --noinput
