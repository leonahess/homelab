
#!/bin/sh

certbot certonly --dns-cloudflare --dns-cloudflare-credentials ~/.secrets/cloudflare.ini -d influx.leona.pink

docker-compose -f /root/homelab/lxc/221-influx/influx.yml down

rm /mnt/influx-certs/fullchain.pem
rm /mnt/influx-certs/privkey.pem

cp /etc/letsencrypt/live/influx.leona.pink/fullchain.pem /mnt/appdata/influx-certs/fullchain.pem
cp /etc/letsencrypt/live/influx.leona.pink/privkey.pem /mnt/appdata/influx-certs/privkey.pem

chown 1000 /mnt/influx-certs/fullchain.pem
chown 1000 /mnt/influx-certs/privkey.pem

docker-compose -f /root/homelab/lxc/221-influx/influx.yml up -d
