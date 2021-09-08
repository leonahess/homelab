
#!/bin/sh

docker-compose -f /root/homelab/lxc/221-influx/influx.yml pull
docker-compose -f /root/homelab/lxc/221-influx/influx.yml down
docker-compose -f /root/homelab/lxc/221-influx/influx.yml up -d
