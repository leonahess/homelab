## Service config

```
     ip:  192.168.66.215
   port:  80
 domain:  audiobook.leona.pink
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

### mount required shares into the lxc

```
pct set 215 -mp0 /mnt/unraid/media/audio/audiobooks,mp=/mnt/bind/media
```

## Service Setup

The service is Audiobookshelf: https://github.com/advplyr/audiobookshelf
The used docker images is here: https://hub.docker.com/r/advplyr/audiobookshelf

### clone homelab repo

```
git clone https://github.com/leonahess/homelab
```

### create appdata directories

```
mkdir -p /mnt/appdata/audiobookshelf/metadata
mkdir -p /mnt/appdata/audiobookshelf/config
```

### start service

```
docker-compose -f /root/homelab/lxc/215-audiobookshelf/docker-compose.yml up -d
```

## Maintenance

You can setup some cronjobs to keep the lxc and the service up to date. For that install the cronjobs found in the crontab file. 

### add cronjob to crontab

```
0 3 * * 0 sh /root/homelab/lxc/215-audiobookshelf/crons/update-ubuntu.sh
0 3 * * 1 sh /root/homelab/lxc/215-audiobookshelf/crons/update-audiobookshelf.sh
```
