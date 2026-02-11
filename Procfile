release: python manage.py migrate --noinput
web: python create_admin.py; gunicorn nieruchomosci.wsgi --bind 0.0.0.0:$PORT --log-file -
