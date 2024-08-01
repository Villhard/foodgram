#!/bin/sh

python manage.py makemigrations
python manage.py migrate --no-input
python manage.py load_ingredients
python manage.py collectstatic --no-input
cp -r /app/collected_static/. /backend_static/build/static/

gunicorn --bind :8000 backend.wsgi