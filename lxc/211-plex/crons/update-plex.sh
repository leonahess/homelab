#!/bin/sh

docker-compose -f /root/homelab/lxc/227-homeassistant/docker-compose.yml pull
docker-compose -f /root/homelab/lxc/227-homeassistant/docker-compose.yml up -d
docker image prune -f
