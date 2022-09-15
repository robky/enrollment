#!/bin/sh

docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createcachetable
docker-compose exec web python manage.py collectstatic  --noinput
docker-compose exec web python manage.py createsuperuser