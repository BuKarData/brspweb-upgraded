release: python manage.py migrate --noinput
web: python manage.py createsuperuser --noinput --username PawelW --email admin@example.com || true && gunicorn nieruchomosci.wsgi --log-file -