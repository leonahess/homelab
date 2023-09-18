#!/bin/sh

certbot certonly --dns-cloudflare --dns-cloudflare-credentials ~/.secrets/cloudflare.ini -d prometheus.leona.pink
certbot certonly --dns-cloudflare --dns-cloudflare-credentials ~/.secrets/cloudflare.ini -d alertmanager.leona.pink


docker-compose -f /root/homelab/lxc/226-prometheus/docker-compose.yml down

rm /mnt/appdata/prometheus/fullchain.pem
rm /mnt/appdata/prometheus/privkey.pem

rm /mnt/appdata/alertmanager/fullchain.pem
rm /mnt/appdata/alertmanager/privkey.pem

cp /etc/letsencrypt/live/prometheus.leona.pink/fullchain.pem /mnt/appdata/prometheus/fullchain.pem
cp /etc/letsencrypt/live/prometheus.leona.pink/privkey.pem /mnt/appdata/prometheus/privkey.pem

cp /etc/letsencrypt/live/alertmanager.leona.pink/fullchain.pem /mnt/appdata/alertmanager/fullchain.pem
cp /etc/letsencrypt/live/alertmanager.leona.pink/privkey.pem /mnt/appdata/alertmanager/privkey.pem

chown 472 /mnt/appdata/prometheus/fullchain.pem
chown 472 /mnt/appdata/prometheus/privkey.pem

chown 472 /mnt/appdata/alertmanager/fullchain.pem
chown 472 /mnt/appdata/alertmanager/privkey.pem


docker-compose -f /root/homelab/lxc/222-grafana/docker-compose.yml up -d
