#!/bin/sh

certbot certonly --dns-cloudflare --dns-cloudflare-credentials ~/.secrets/cloudflare.ini -d homeassistant.leona.pink

docker-compose -f /root/homelab/lxc/227-homeassistant/docker-compose.yml down

rm /mnt/appdata/nginx/fullchain.pem
rm /mnt/appdata/nginx/privkey.pem

cp /etc/letsencrypt/live/homeassistant.leona.pink/fullchain.pem /mnt/appdata/nginx/fullchain.pem
cp /etc/letsencrypt/live/homeassistant.leona.pink/privkey.pem /mnt/appdata/nginx/privkey.pem

chown 472 /mnt/appdata/nginx/fullchain.pem
chown 472 /mnt/appdata/nginx/privkey.pem

docker-compose -f /root/homelab/lxc/227-homeassistant/docker-compose.yml up -d
