## Service config

```
webPort:  443
     ip:  192.168.66.222
 domain:  grafana.leona.pink
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

### Restart docker

```
systemctl restart docker
```


## Service Setup

The service is grafan, a tool to visualize time series data with ease.
The used docker images is here: https://hub.docker.com/r/grafana/grafana

### clone homelab repo

```
git clone https://github.com/leonahess/homelab
```

### create appdata directories

```
mkdir /mnt/appdata
mkdir /mnt/appdata/grafana
```

### chown the appdata directory to the grafana container user

```
chown 472 /mnt/appdata/grafana
```

### start service

```
docker-compose -f /root/homelab/lxc/222-grafana/docker-compose.yml up -d
```

## Maintenance

You can setup some cronjobs to keep the lxc up to date. For that install the cronjob found in the crontab file. Unfortunately Grafana doesn't have a general version tag like `8.0` to get all minor version updates to version 8.0, 
so updates to the service need to be done manually.

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
certbot certonly --dns-cloudflare --dns-cloudflare-credentials ~/.secrets/cloudflare.ini -d grafana.leona.pink
```

### copy certs to docker bind mount and chown to grafana user

```
cp /etc/letsencrypt/live/grafana.leona.pink/fullchain.pem /mnt/appdata/grafana/fullchain.pem
cp /etc/letsencrypt/live/grafana.leona.pink/privkey.pem /mnt/appdata/grafana/privkey.pem

chown 472 /mnt/appdata/grafana/fullchain.pem
chown 472 /mnt/appdata/grafana/privkey.pem
```

### add cronjob to crontab

```
0 1 1 * * sh /root/homelab/lxc/222-grafana/crons/certbot.sh
```
