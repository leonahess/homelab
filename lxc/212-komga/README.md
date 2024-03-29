## Service config

```
     ip:  192.168.66.212
 domain:  komga.leona.pink
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

### if zfs as storage do this: https://c-goes.github.io/posts/proxmox-lxc-docker-fuse-overlayfs/

1. download latest release: https://github.com/containers/fuse-overlayfs/releases
2. move the binary
```
mv fuse-overlayfs-x86_64 /usr/local/bin/fuse-overlayfs
chmod +x /usr/local/bin/fuse-overlayfs
```
3. set `/etc/docker/daemon.json` (see below)

### Set json logging in docker
Add the following to `/etc/docker/daemon.json`
```
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3",
    "tag": "{{.ImageName}}|{{.Name}}|{{.ImageFullID}}|{{.FullID}}"
  },
  "storage-driver": "fuse-overlayfs"
}
```

### Restart docker

```
systemctl restart docker
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
mkdir /mnt/appdata/komga
```

### start service

```
docker-compose -f /root/homelab/lxc/212-komga/docker-compose.yml up -d
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
