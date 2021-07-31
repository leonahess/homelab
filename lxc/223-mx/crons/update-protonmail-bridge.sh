#!/bin/sh

docker-compose -f /root/docker-compose-db/protonmail-bridge.yml pull
docker-compose -f /root/docker-compose-db/protonmail-bridge.yml down
docker-compose -f /root/docker-compose-db/protonmail-bridge.yml up -d
