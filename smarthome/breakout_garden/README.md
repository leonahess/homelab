# Script to read two various sensors from Pimoroni's breakout garden kit sensors and write to InfluxDB


- https://github.com/pimoroni/bme680-python
- https://github.com/pimoroni/sgp30-python
- https://docs.influxdata.com/influxdb/v2.0/api-guide/client-libraries/python/

## Setup the Pi

```
sudo apt update && sudo apt upgrade -y
cd ~
git clone https://github.com/leonahess/homelab.git
```

## Setup the script

Create .env file in /home/pi/homelab/smarthome/bme688/src
```
nano /home/pi/homelab/smarthome/bme688/src/.env
```

.env file:
```
ROOM=kitchen

SGP30_SENSOR=0
VEML6075_SENSOR=0
BME688_SENSOR_PRIMARY=0
BME688_SENSOR_SECONDARY=0

SGP30_SENSOR_TAG_LOCATION=leona_desk
VEML6075_SENSOR_TAG_LOCATION=leona_desk
BME688_SENSOR_PRIMARY_TAG_LOCATION=leona_desk1
BME688_SENSOR_SECONDARY_TAG_LOCATION=leona_desk2
```

Install python modules
```
pip3 install -r requirements.txt
```

Move service to /etc/systemd/system and start it
```
sudo cp /home/pi/homelab/smarthome/breakout_garden/breakout.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable breakout.service
sudo systemctl start breakout.service
```
