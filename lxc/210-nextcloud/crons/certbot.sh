#!/bin/sh

certbot certonly --dns-cloudflare --dns-cloudflare-credentials ~/.secrets/cloudflare.ini -d nextcloud.leona.pink

docker-compose -f /root/homelab/lxc/210-nextcloud/nextcloud.yml down

rm /mnt/appdata/nextcloud/keys/cert.crt
rm /mnt/appdata/nextcloud/keys/cert.key

cp /etc/letsencrypt/live/nextcloud.leona.pink/fullchain.pem /mnt/appdata/nextcloud/keys/cert.crt
cp /etc/letsencrypt/live/nextcloud.leona.pink/privkey.pem /mnt/appdata/nextcloud/keys/cert.key

chown 99 /mnt/appdata/nextcloud/keys/cert.crt
chgrp 100 /mnt/appdata/nextcloud/keys/cert.crt

chown 99 /mnt/appdata/nextcloud/keys/cert.key
chgrp 100 /mnt/appdata/nextcloud/keys/cert.key

docker-compose -f /root/homelab/lxc/210-nextcloud/nextcloud.yml up -d
