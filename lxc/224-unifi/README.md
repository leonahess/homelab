## Service config

```
webPort:  8443
     ip:  192.168.66.224
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

The service is the unifi controller, to manage all unifi devices in the network.
The used docker images is here: https://hub.docker.com/r/linuxserver/unifi-controller

### clone homelab repo

```
git clone https://github.com/leonahess/homelab
```

### create appdata directories

```
mkdir /mnt/appdata
mkdir /mnt/appdata/unifi
```

### start service

```
docker-compose -f /root/homelab/lxc/224-unifi/docker-compose.yml up -d
```

## Maintenance

You can setup some cronjobs to keep the lxc up to date. For that install the cronjob found in the crontab file.
