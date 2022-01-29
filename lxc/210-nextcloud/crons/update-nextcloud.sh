#!/bin/sh

docker-compose -f /root/homelab/lxc/210-nextcloud/docker-compose.yml pull
docker-compose -f /root/homelab/lxc/210-nextcloud/docker-compose.yml up -d
docker image prune -f
