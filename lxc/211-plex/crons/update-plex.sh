#!/bin/sh

docker-compose -f /root/homelab/lxc/211-plex/plex.yml pull
docker-compose -f /root/homelab/lxc/211-plex/plex.yml down
docker-compose -f /root/homelab/lxc/211-plex/plex.yml up -d
docker image prune -f
