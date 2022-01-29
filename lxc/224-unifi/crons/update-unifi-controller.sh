#!/bin/sh

docker-compose -f /root/homelab/lxc/224-unifi/docker-compose.yml pull
docker-compose -f /root/homelab/lxc/224-unifi/docker-compose.yml up -d
docker image prune -f
