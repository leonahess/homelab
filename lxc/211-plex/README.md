## Service config

```
     ip:  192.168.66.211
 domain:  plex.leona.pink
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

### mount required shares into the lxc

```
pct set 211 -mp0 /mnt/unraid/media,mp=/mnt/bind/media
```

## Service Setup

The service is the Plex Media Server.
The used docker images is here: https://hub.docker.com/r/linuxserver/unifi-controller

### clone homelab repo

```
git clone https://github.com/leonahess/homelab
```

### create appdata directories

```
mkdir /mnt/appdata
mkdir /mnt/appdata/plexmediaserver
```

### create .env with the following in the `211-plex` folder:

```
TZ="Europe/Berlin"
PLEX_CLAIM="YOUR-PLEX-CLAIM"
PLEX_UID=99
PLEX_GID=100
```

### start service

```
docker-compose -f /root/homelab/lxc/211-plex/plex.yml up -d
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
certbot certonly --dns-cloudflare --dns-cloudflare-credentials ~/.secrets/cloudflare.ini -d plex.leona.pink
```

### convert to pkcs12

```
openssl pkcs12 -export -out /mnt/appdata/plexmediaserver/Library/Application\ Support/Plex\ Media\ Server/cert.pfx -inkey /etc/letsencrypt/live/plex.leona.pink/privkey.pem -in /etc/letsencrypt/live/plex.leona.pink/cert.pem -certfile /etc/letsencrypt/live/plex.leona.pink/chain.pem
```

### chown and chgrp to plex user and group

```
chown 99 /mnt/appdata/plexmediaserver/Library/Application\ Support/Plex\ Media\ Server/cert.pfx
chgrp 100 /mnt/appdata/plexmediaserver/Library/Application\ Support/Plex\ Media\ Server/cert.pfx
```

### add cronjob to crontab

```
0 1 1 * * sh /root/homelab/lxc/211-plex/crons/certbot.sh
```
