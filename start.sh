#!/bin/bash
set -e

echo "=== Collectstatic ==="
python manage.py collectstatic --noinput --clear

echo "=== Migrations ==="
python manage.py migrate --noinput

echo "=== Create admin ==="
python create_admin.py

echo "=== Starting gunicorn with scheduler ==="
export RUN_SCHEDULER=true
exec gunicorn nieruchomosci.wsgi --bind 0.0.0.0:${PORT:-8080} --log-file -
