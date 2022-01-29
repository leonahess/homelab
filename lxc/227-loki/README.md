## Service config

```
     ip:  192.168.66.227
   port:  3100
 domain:  loki.leona.pink
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
    "max-file": "3" 
  }
}
```

### Restart docker

```
systemctl restart docker
```

## Service Setup

The service is Loki, a a log aggregation tool.
The used docker images is here: https://hub.docker.com/r/grafana/loki

### clone homelab repo

```
git clone https://github.com/leonahess/homelab
```

### create appdata directories

```
mkdir -p /mnt/appdata/loki
```


### start service

```
docker-compose -f /root/homelab/lxc/227-loki/docker-compose.yml up -d
```
