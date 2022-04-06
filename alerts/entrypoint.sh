#!/bin/bash
set -e

case "$1" in
    test)
        python manage.py test --no-input
        ;;
    start)
        python manage.py makemigrations
        python manage.py migrate
        python manage.py createsuperuser --noinput || true
        python manage.py runserver 0.0.0.0:8080
        ;;
    *)
        exec "$@"
        ;;
esac
