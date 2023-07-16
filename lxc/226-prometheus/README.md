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

### start service

```
docker-compose -f /root/homelab/lxc/226-prometheus/docker-compose.yml up -d
```

# Exporters
A list of all Exporters used, their function and configuration.

## [Blackbox Exporter](https://github.com/prometheus/blackbox_exporter/):
Probe HTTP/S endpoints to check service availability.

#### Services to Query:
```
# Nextcloud
https://nextcloud.leona.pink/login

# Homeassistant
http://homeassistant.leona.pink:8123

# Unifi Controller
https://unifi.leona.pink/manage/account/login

# Grafana
https://grafana.leona.pink/login

# Prometheus
http://prometheus.leona.pink:9090/graph

# Unraid UI
https://fx8350.leona.pink/login

# Proxbox UI
https://tinyprox1.leona.pink:8006
```

#### exporter-config/blackbox.yml:
```yml
modules:
  http_2xx:
    prober: http
    timeout: 5s
    http:
      valid_http_versions: ["HTTP/1.1", "HTTP/2.0"]
      valid_status_codes: []  # Defaults to 2xx
      method: GET
      headers:
        Host: prometheus.leona.pink
        Origin: leona.pink
      follow_redirects: true
      fail_if_ssl: false
      fail_if_not_ssl: false
      tls_config:
        insecure_skip_verify: true
      preferred_ip_protocol: "ip4" # defaults to "ip6"
      ip_protocol_fallback: false  # no fallback to "ip6"
```

#### docker-compose.yml:
```yml
  blackbox:
    image: prom/blackbox-exporter
    container_name: blackbox-exporter
    ports:
      - 9115:9115
    command:
      - --config.file=/etc/blackbox/blackbox.yml
    volumes:
      - /root/homelab/lxc/226-prometheus/exporter-config/blackbox.yml:/etc/blackbox/blackbox.yml
```

#### prometheus.yml:
```yml
  - job_name: 'blackbox'
    metrics_path: /probe
    params:
      module: [http_2xx]  # Look for a HTTP 200 response.
    static_configs:
      - targets:
        - https://nextcloud.leona.pink/login
        - http://homeassistant.leona.pink:8123
        - https://unifi.leona.pink/manage/account/login
        - https://grafana.leona.pink/login
        - http://prometheus.leona.pink:9090/graph
        - https://fx8350.leona.pink/login
        - https://tinyprox1.leona.pink:8006
    relabel_configs:
      - source_labels: [__address__]
        target_label: __param_target
      - source_labels: [__param_target]
        target_label: instance
      - target_label: __address__
        replacement: blackbox-exporter:9115  # The blackbox exporter's real hostname:port.
```

## [Node Exporter](https://github.com/prometheus/node_exporter):
Gets node metrics. Needs to be installed on each node to be monitored.

#### prometheus.yml:
````yml
  - job_name: 'nodes_services'
    scrape_interval: 5s
    static_configs:
      - targets:
        - dns.leona.pink:9100
        - filer.leona.pink:9100
        - fx8350.leona.pink:9100
        - tinyprox1.leona.pink:9100

  - job_name: 'nodes_iot'
    scrape_interval: 5s
    static_configs:
      - targets:
          - enviro1.leona.pink:9100
          - enviro2.leona.pink:9100
          - enviro3.leona.pink:9100
          - breakout1.leona.pink:9100
          - breakout2.leona.pink:9100
          - breakout3.leona.pink:9100
````

## [Unifi-Poller](https://github.com/unpoller/unpoller):
Gets metrics from the unifi controller.

#### exporter-config/.unpoller.env:
```
UP_INFLUXDB_DISABLE=true
UP_UNIFI_DYNAMIC=true
UP_PROMETHEUS_HTTP_LISTEN=0.0.0.0:9130
UP_PROMETHEUS_NAMESPACE=unifipoller
UP_UNIFI_DEFAULT_USER=me
UP_UNIFI_DEFAULT_PASS=redacted
```

#### docker-compose.yml:
````yml
  unpoller:
    container_name: unpoller
    restart: unless-stopped
    image: golift/unifi-poller:latest
    ports:
      - 9130:9130
    env_file:
      - exporter-config/.unpoller.env
````

#### prometheus.yml:
````yml
  - job_name: 'unifipoller'
    scrape_interval: 5s
    static_configs:
      - targets:
        - https://unifi.leona.pink:443
    metrics_path: /scrape
    relabel_configs:
     - source_labels: [__address__]
       target_label: __param_target
     - source_labels: [__param_target]
       target_label: instance
     - target_label: __address__
       replacement: unpoller:9130
````


## prometheus-pve-exporter:

Create `pve.yml` with the following data:
```
default:
    user: prometheus@pve
    password: redacted
    verify_ssl: true
```


## nextcloud Exporter:


## IOT Exporters:

### Tapo P110
Gets metrics from the TP-Link Tapo P110 smart power plugs.

#### exporter-config/.tapo-x.env:
````env
IP=redacted
USERNAME=redacted
PASSWORD=redacted
LOCATION=desk
ROOM=Rabusche
DEVICE=Rechner
IS_LIGHT=false
TYPE=Device
````

#### docker-compose.yml:
````yaml
  tapo-x:
    build: ../../smarthome/tapo_p110
    image: tapo_p110:latest
    env_file: exporter-config/.tapo-x.env
    container_name: tapo-x
    restart: unless-stopped
    ports:
      - 8000:8000
````

#### prometheus.yml:
````yaml
  - job_name: 'tapo_p110'
    scrape_interval: 5s
    static_configs:
      - targets:
        - tapo-1:8000
        - tapo-2:8000
        - tapo-3:8000
        - tapo-4:8000
        - tapo-5:8000
        - tapo-6:8000
        - tapo-7:8000
        - tapo-8:8000
        - tapo-9:8000
        - tapo-10:8000
        - tapo-11:8000
        - tapo-12:8000
````

### Enviro
Gets metrics from Pimoroni Enviro Raspi Hat. Exporter is installed and configured on Raspi.

#### prometheus.yml:
````yml
  - job_name: 'enviro'
    scrape_interval: 1s
    static_configs:
      - targets:
        - enviro3.leona.pink:8000
        - enviro2.leona.pink:8000
````

### Breakout
Gets metrics from Pimoroni Breakout Raspi Hat. Exporter is installed and configured on Raspi.

#### prometheus.yml:
`````yml
  - job_name: 'breakout'
    scrape_interval: 1s
    static_configs:
      - targets:
        - breakout1.leona.pink:8003
        - breakout2.leona.pink:8003
        - breakout3.leona.pink:8003
`````

### SCD30
Gets metrics from the SCD30 CO2 sensor. Exporter is installed and configured on Raspi.

#### prometheus.yml:
````yml
  - job_name: 'scd30'
    scrape_interval: 1s
    static_configs:
      - targets:
        - enviro1.leona.pink:8001
````