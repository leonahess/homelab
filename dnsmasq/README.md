I run a dnsmasq instance on a Raspberry Pi 3B+. For now it only serves as a DNS server.

## Service config

```
ip: 192.168.66.2
```

## Services setup

### install tools

```
sudo apt install git dnsmasq
```

### clone homelab repo

```
cd ~
git clone https://github.com/leonahess/homelab
```

### copy hosts and config file

```
cp /home/pi/homelab/dnsmasq/hosts /etc/hosts
cp /home/pi/homelab/dnsmasq/dnsmasq.conf /etc/dnsmasq.conf
```

### restart dnsmasq to load new config

```
sudo systemctl restart dnsmasq
```
