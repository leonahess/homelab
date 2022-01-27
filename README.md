# homelab
This repository has a collection of notes, configs and the likes I use to run my homelab.

# General Setup
## Proxmox Hyperconverged Cluster
Runs most services in the homelab. All services run in docker containers inside of LXC containers. A Ceph cluster allows for redundant and easily migratable storage of all services. A 10 gbit/s connection allows for a high cluster performance. See the `lxc` folder for templates of the different services.

### Sofware

```text
OS: Proxmox VE 7
CEPH: 16.2
```

### Hardware 

```text
CPUs: 18c/18t
RAM: 96 GB @ 2133 MHz
Storage:
  boot: 1,25 TB
  ceph: 3 TB (1 TB usable because of three way replication)
NET: 10 gbit SFP+
```

#### Lenovo m920x tiny:

```text
CPU: Intel i5-8400 - 6c/6t @ 2,8/4,0 GHz - 65 W
RAM: 64 GB @ 2133 MHz
Storage:
  boot: 256 GB Samsung (nvme)
  ceph: 1 TB Kioxia Excercia Plus (nvme)
NIC: Mellanox ConnectX-3 - 1 SFP+ Port
```

#### Lenovo m920q tiny:

```text
CPU: Intel i5-8500T - 6c/6t @ 2,1/3,5 GHz - 35 W
RAM: 16GB @ 2133 MHz
Storage:
  boot: 500 GB Samsung 840 EVO (SATA)
  ceph: 1 TB Kioxia Excercia Plus (nvme)
NIC: Mellanox ConnectX-3 - 1 SFP+ Port
```

#### Lenovo m720q tiny:

```text
CPU: Intel i5-8500T - 6c/6t @ 2,1/3,5 GHz - 35 W
RAM: 16 GB @ 2133 MHz
Storage:
  boot: 500 GB Samsung 840 EVO (SATA)
  ceph: 1 TB Kioxia Excercia Plus (nvme)
NIC: Mellanox ConnectX-3 - 1 SFP+ Port
```

## Unraid Box
Current backup solution and mass storage device. Connected via a 10 gbit/s link for fast backup speeds. Due to Unraids storage architecture the link is not fully utilized as the max speed achieved by the array is the max speed of a given hard disk drive.

### Software

```text
OS: Unraid 6.9
```

### Hardware

```text
CPU: AMD FX-8350 - 8c/8t @4,0 GHz
RAM: 16 GB @ 1600 MHz
Storage:
  boot: 32 GB Flash Drive
  mass storage: 4 x 8 TB WD HDD (24 TB usable)
NIC: Mellanox ConnectX-2 - 1 SFP+ Port
GPU: NVIDIA GT 1030
Case: 4U Inter Tech Rack case
```

## Currently unused Hardware
#### Dell R510:

```text
CPU: 2 x Intel X5660 - 6c/12t @ 2,8/3,2 GHz - 95 W
RAM: 96 GB @ 1033 MHz
Storage:
  boot: 120 GB Samsung SSD (SATA)
  mass storage: 8 x 2 TB HDD
NIC: Mellanox ConnectX-2
```

#### Custom Box

```text
CPU: 2 x Intel X5660 - 6c/12t @ 2,8/3,2 GHz - 95 W
RAM: 96 GB @ 1033 MHz
Storage:
  boot: none
NIC: HP 2 x SFP+ card
Case: 4U Inter Tech Rack case
```

## DNS Raspi
A Raspberry Pi 3 B+ running dnsmasq to provide the whole home network with DNS services. See the `dnsmasq` folder for the dnsmasq config and `hosts` file.

## Smarthome Raspis
4 Raspberrry Pi 3 B+ running a assortment of sensors to measure room temperature, humidity, etc. See the `smarthome` folders for the prometheus exporters running of the Raspis. Prometheus is used to scrape the exporters and Grafana to visualize the data.

## Network
### Switches
#### Ubiquity USW-Aggregation
10 G backbone with 8 SFP+ ports.

#### Netgear GS724T
24 Port Gigabit switch for general connectivity.

### Router
Just a FritzBox
