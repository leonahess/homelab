#!/bin/sh

certbot certonly --dns-cloudflare --dns-cloudflare-credentials ~/.secrets/cloudflare.ini -d prometheus.leona.pink
certbot certonly --dns-cloudflare --dns-cloudflare-credentials ~/.secrets/cloudflare.ini -d alertmanager.leona.pink


docker-compose -f /root/homelab/lxc/226-prometheus/docker-compose.yml down

rm /mnt/appdata/nginx/prometheus/fullchain.pem
rm /mnt/appdata/nginx/prometheus/privkey.pem

rm /mnt/appdata/nginx/alertmanager/fullchain.pem
rm /mnt/appdata/nginx/alertmanager/privkey.pem

cp /etc/letsencrypt/live/prometheus.leona.pink/fullchain.pem /mnt/appdata/nginx/prometheus/fullchain.pem
cp /etc/letsencrypt/live/prometheus.leona.pink/privkey.pem /mnt/appdata/nginx/prometheus/privkey.pem

cp /etc/letsencrypt/live/alertmanager.leona.pink/fullchain.pem /mnt/appdata/nginx/alertmanager/fullchain.pem
cp /etc/letsencrypt/live/alertmanager.leona.pink/privkey.pem /mnt/appdata/nginx/alertmanager/privkey.pem

chown 472 /mnt/appdata/nginx/prometheus/fullchain.pem
chown 472 /mnt/appdata/nginx/prometheus/privkey.pem

chown 472 /mnt/appdata/nginx/alertmanager/fullchain.pem
chown 472 /mnt/appdata/nginx/alertmanager/privkey.pem


docker-compose -f /root/homelab/lxc/222-grafana/docker-compose.yml up -d
