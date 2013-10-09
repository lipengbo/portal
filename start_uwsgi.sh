uwsgi --module=ccf.wsgi:application --env DJANGO_SETTINGS_MODULE=ccf.settings --socket=127.0.0.1:49152 &
