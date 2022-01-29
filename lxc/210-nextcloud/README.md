## Service config

```
     ip:  192.168.66.210
 domain:  nextcloud.leona.pink
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

### Set json logging in docker
Add the following to `/etc/docker/daemon.json`
```
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3",
    "tag": "{{.ImageName}}|{{.Name}}|{{.ImageFullID}}|{{.FullID}}"
  }
}
```

### mount required shares into the lxc

```
pct set 210 -mp0 /mnt/pve/cephfs/nextcloud-data,mp=/mnt/nextcloud-data,shared=1
```

## Service Setup

The service is Nextcloud.
The used docker images is here: https://docs.linuxserver.io/images/docker-nextcloud

### clone homelab repo

```
git clone https://github.com/leonahess/homelab
```

### create appdata directories

```
mkdir /mnt/appdata
mkdir /mnt/appdata/nextcloud
mkdir /mnt/appdata/nextcloud-db
```

### create .env with the following in the `210-nextcloud` folder:

```
PUID=99
PGID=100
MYSQL_ROOT_PASSWORD=YOUR_ROOT_PW
TZ=Europe/Berlin
MYSQL_DATABASE=nextcloud
MYSQL_USER=nextcloud
MYSQL_PASSWORD=YOUR_SQL_PW
```

### start service

```
docker-compose -f /root/homelab/lxc/210-nextcloud/docker-compose.yml up -d
```

## Maintenance

You can setup some cronjobs to keep the lxc and the service up to date. For that install the cronjobs found in the crontab file. 

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

### get certs

```
certbot certonly --dns-cloudflare --dns-cloudflare-credentials ~/.secrets/cloudflare.ini -d nextcloud.leona.pink
```

### chown and chgrp to plex user and group

```
cp /etc/letsencrypt/live/nextcloud.leona.pink/fullchain.pem /mnt/appdata/nextcloud/keys/cert.crt
cp /etc/letsencrypt/live/nextcloud.leona.pink/privkey.pem /mnt/appdata/nextcloud/keys/cert.key


chown 99 /mnt/appdata/nextcloud/keys/cert.crt
chgrp 100 /mnt/appdata/nextcloud/keys/cert.crt

chown 99 /mnt/appdata/nextcloud/keys/cert.key
chgrp 100 /mnt/appdata/nextcloud/keys/cert.key
```

### add cronjob to crontab

```
0 1 1 * * sh /root/homelab/lxc/210-plex/crons/certbot.sh
```
