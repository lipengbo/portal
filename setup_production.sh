./manage.py syncdb
./manage.py migrate --no-initial-data
./manage.py loaddata fixtures/initial.json
read -p "Would you like to create a super user? (y/n): " IS_CREATE
if [[ $IS_CREATE =~ ^[Yy](es)*$ ]]; then
    ./manage.py createsuperuser
fi
./manage.py reset_domain
./manage.py collectstatic --noinput

