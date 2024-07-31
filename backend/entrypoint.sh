#!/bin/sh

python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic
cp -r /app/collected_static/. /backend_static/build/static/

gunicorn --bind :8000 backend.wsgi