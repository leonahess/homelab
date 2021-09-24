#!/bin/sh

docker-compose -f /root/homelab/lxc/223-mx/protonmail-bridge.yml pull
docker-compose -f /root/homelab/lxc/223-mx/protonmail-bridge.yml down
docker-compose -f /root/homelab/lxc/223-mx/protonmail-bridge.yml up -d
docker image prune -f
