## Service config

```
webPort:  8086
 dbPort:  8086
     ip:  192.168.66.221
 domain:  unifi.leona.pink
```

## LXC Setup

### update OS

```
apt update && apt upgrade -y && apt autoremove -y
```

### install tools

```
apt install curl git docker-compose
```

### install docker

```
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```


## Service Setup

The service is InfluxDB, a time series database.
The used docker images is here: https://hub.docker.com/_/influxdb

### clone homelab repo

```
git clone https://github.com/leonahess/homelab
```

### create appdata directories

```
mkdir /mnt/appdata/influx
mkidr /mnt/appdata/influx-certs
```

### start service

```
docker-compose -f /root/homelab/lxc/221-influx/influx.yml up -d
```

## Maintenance

You can setup some cronjobs to keep the lxc and service up to date. For that install the cronjob found in the crontab file.

## SSL Certs

### Install certbot and cloudflare plugin

```
apt install certbot python3-certbot-dns-cloudflare
```

### Create cloudflare.ini with cloudflare credentials

cloudflare.ini
```
dns_cloudflare_email=insert_your_email_here
dns_cloudflare_api_key=insert_your_global_api_key_here
```

chmod to 600

```
chmod 600 /root/.secrets/cloudflare.ini
```

### get certs

```
certbot certonly --dns-cloudflare --dns-cloudflare-credentials ~/.secrets/cloudflare.ini -d influx.leona.pink
```

### copy certs to docker bind mount and chown to grafana user

```
cp /etc/letsencrypt/live/influx.leona.pink/fullchain.pem /mnt/appdata/influx-certs/fullchain.pem
cp /etc/letsencrypt/live/influx.leona.pink/privkey.pem /mnt/appdata/influx-certs/privkey.pem

chown 1000 /mnt/influx-certs/fullchain.pem
chown 1000 /mnt/influx-certs/privkey.pem
```

### add cronjob to crontab

```
0 1 1 * * sh /root/homelab/lxc/221-influx/crons/certbot.sh
```
