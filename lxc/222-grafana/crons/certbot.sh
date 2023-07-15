#!/bin/sh

certbot certonly --dns-cloudflare --dns-cloudflare-credentials ~/.secrets/cloudflare.ini -d grafana.leona.pink

docker-compose -f /root/homelab/lxc/222-grafana/docker-compose.yml down

rm /mnt/appdata/grafana/fullchain.pem
rm /mnt/appdata/grafana/privkey.pem

cp /etc/letsencrypt/live/grafana.leona.pink/fullchain.pem /mnt/appdata/grafana/fullchain.pem
cp /etc/letsencrypt/live/grafana.leona.pink/privkey.pem /mnt/appdata/grafana/privkey.pem

chown 472 /mnt/appdata/grafana/fullchain.pem
chown 472 /mnt/appdata/grafana/privkey.pem

docker-compose -f /root/homelab/lxc/222-grafana/docker-compose.yml up -d
