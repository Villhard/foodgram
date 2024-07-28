#!/bin/sh

python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic

gunicorn --bind :8000 backend.wsgi