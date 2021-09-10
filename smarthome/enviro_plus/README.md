# Script to read Pimoroni's Enviroplus Hat and write to InfluxDB


- https://github.com/pimoroni/enviroplus-python
- https://docs.influxdata.com/influxdb/v2.0/api-guide/client-libraries/python/

## Setup the Pi

```
sudo apt update && sudo apt upgrade -y
cd ~
git clone https://github.com/leonahess/homelab.git
```

Use the enviro setup script to configure i2c, etc
```
git clone https://github.com/pimoroni/enviroplus-python
cd enviroplus-python
sudo ./install.sh
```

## Setup the script

Create .env file in /home/pi/homelab/smarthome/enviro_plus/src
```
nano /home/pi/homelab/smarthome/enviro_plus/src/.env
```

.env file:
```
INFLUX_BUCKET=smarthome
INFLUX_ORG=me
INFLUX_TOKEN=add_your_influx_token_here
INFLUX_URL=https://influx.leona.pink:8086
TAG_LOCATION=leona_backyard
PM_SENSOR=True
```

Install python modules
```
pip3 install -r requirements.txt
```

Move service to /etc/systemd/system and start it
```
sudo cp /home/pi/homelab/smarthome/enviro_plus/enviro.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable enviro.service
sudo systemctl start envrio.service
```
