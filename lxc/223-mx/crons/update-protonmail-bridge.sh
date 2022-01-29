#!/bin/sh

docker-compose -f /root/homelab/lxc/223-mx/docker-compose.yml pull
docker-compose -f /root/homelab/lxc/223-mx/docker-compose.yml up -d
docker image prune -f
