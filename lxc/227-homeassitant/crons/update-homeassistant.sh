#!/bin/sh

docker-compose -f /root/homelab/lxc/211-plex/docker-compose.yml pull
docker-compose -f /root/homelab/lxc/211-plex/docker-compose.yml up -d
docker image prune -f
