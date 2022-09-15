#!/bin/sh

docker-compose stop
docker-compose rm -f web
docker rmi $(docker images robky/enrollment -q)
docker-compose up -d --build