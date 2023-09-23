## Service config

```
     ip:  192.168.66.227
     port:  8123
   domain:  homeassistant.leona.pink
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

## Service Setup

The service is Homeassistant.

### clone homelab repo

```
git clone https://github.com/leonahess/homelab
```

### create appdata directories

```
mkdir -p /mnt/appdata/homeassistant
```

### start service

```
docker-compose -f /root/homelab/lxc/227-homeassistant/docker-compose.yml up -d
```

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
certbot certonly --dns-cloudflare --dns-cloudflare-credentials ~/.secrets/cloudflare.ini -d homeassistant.leona.pink
```

### copy certs to docker bind mount and chown to grafana user

```
cp /etc/letsencrypt/live/homeassistant.leona.pink/fullchain.pem /mnt/appdata/nginx/fullchain.pem
cp /etc/letsencrypt/live/homeassistant.leona.pink/privkey.pem /mnt/appdata/nginx/privkey.pem

chown 472 /mnt/appdata/nginx/fullchain.pem
chown 472 /mnt/appdata/nginx/privkey.pem
```

### add cronjob to crontab

```
0 1 1 * * sh /root/homelab/lxc/227-homeassistant/crons/certbot.sh
```