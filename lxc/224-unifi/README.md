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
docker-compose -f /root/homelab/lxc/224-unifi/unifi-controller.yml up -d
```

## Maintenance

You can setup some cronjobs to keep the lxc up to date. For that install the cronjob found in the crontab file. Unfortunately Grafana doesn't have a general version tag like `8.0` to get all minor version updates to version 8.0, 
so updates to the service need to be done manually.
