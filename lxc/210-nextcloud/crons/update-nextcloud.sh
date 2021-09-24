#!/bin/sh

docker-compose -f /root/homelab/lxc/210-nextcloud/nextcloud.yml pull
docker-compose -f /root/homelab/lxc/210-nextcloud/nextcloud.yml down
docker-compose -f /root/homelab/lxc/210-nextcloud/nextcloud.yml up -d
docker image prune -f
