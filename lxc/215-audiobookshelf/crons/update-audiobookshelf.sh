#!/bin/sh

docker-compose -f /root/homelab/lxc/215-audiobookshelf/audiobookshelf.yml pull
docker-compose -f /root/homelab/lxc/215-audiobookshelf/audiobookshelf.yml up -d
docker image prune -f
