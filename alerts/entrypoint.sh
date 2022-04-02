#!/bin/bash
set -e

case "$1" in
    start)
        python manage.py makemigrations
        python manage.py migrate
        python manage.py createsuperuser --noinput
        python manage.py runserver 0.0.0.0:8080
        ;;
    *)
        exec "$@"
        ;;
esac
