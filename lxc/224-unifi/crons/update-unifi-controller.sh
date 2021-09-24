#!/bin/sh

docker-compose -f /root/homelab/lxc/224-unifi/unifi-controller.yml pull
docker-compose -f /root/homelab/lxc/224-unifi/unifi-controller.yml down
docker-compose -f /root/homelab/lxc/224-unifi/unifi-controller.yml up -d
docker image prune -f
