#!/bin/sh
rm -rf /app/migrations/*.py
touch /app/migrations/__init__.py
python manage.py makemigrations
python manage.py migrate
