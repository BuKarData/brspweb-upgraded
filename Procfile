release: python manage.py migrate --noinput
web: python manage.py ensure_superuser; gunicorn nieruchomosci.wsgi --bind 0.0.0.0:$PORT --log-file -
