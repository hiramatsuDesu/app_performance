#!/bin/sh
set -e

echo "Creating migrations..."
python manage.py makemigrations --noinput

echo "Applying migrations..."
python manage.py migrate --noinput

if [ "$DEBUG_MODE" = "True" ]; then
    echo "Waiting for VSCode debugger on port 5678..."
    exec python -Xfrozen_modules=off -m debugpy --wait-for-client --listen 0.0.0.0:5678 manage.py runserver 0.0.0.0:8000
else
    echo "Starting Django server normally..."
    exec python manage.py runserver 0.0.0.0:8000
fi
