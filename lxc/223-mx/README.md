## Service config

```
SMTP Port: 1025
IMAP Port: 1143
       ip: 192.168.66.223
   domain: mx.leona.pink
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

The service is the protonmail bridge to provide an SMTP endpoint for protonmail.
The used docker images is here: https://github.com/shenxn/protonmail-bridge-docker

### clone homelab repo

```
git clone https://github.com/leonahess/homelab
```

### create appdata directories

```
mkdir /mnt/appdata
mkdir /mnt/appdata/protonmail-bridge
```

### setup the bridge

see CLI guide here: https://protonmail.com/support/knowledge-base/bridge-cli-guide/

```
docker run --rm -it -v /mnt/appdata/protonmail-bridge:/root shenxn/protonmail-bridge init
```

### start service

```
docker-compose -f /root/homelab/lxc/223-mx/docker-compose.yml up -d
```

## Maintenance

You can setup some cronjobs to keep the lxc and service up to date.
For that install the two cronjobs found in the `crontab` file.

