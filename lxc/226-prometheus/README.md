## Service config

```
     ip:  192.168.66.226
   port:  9090
 domain:  prometheus.leona.pink
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

The service is Prometheus.

### clone homelab repo

```
git clone https://github.com/leonahess/homelab
```

### create appdata directories

```
mkdir -p /mnt/appdata/prometheus
```

### create config files

#### pve exporter
Create `pve.yml` with the following data:
```
default:
    user: prometheus@pve
    password: redacted
    verify_ssl: true
```

#### unpoller exporter
Create `.env` with the following data:
```
UP_INFLUXDB_DISABLE=true
UP_UNIFI_DYNAMIC=true
UP_PROMETHEUS_HTTP_LISTEN=0.0.0.0:9130
UP_PROMETHEUS_NAMESPACE=unifipoller
UP_UNIFI_DEFAULT_USER=me
UP_UNIFI_DEFAULT_PASS=redacted
```

### start service

```
docker-compose -f /root/homelab/lxc/226-prometheus/docker-compose.yml up -d
```
