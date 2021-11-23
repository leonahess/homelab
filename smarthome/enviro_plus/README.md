# Script to read Pimoroni's Enviroplus Hat and expose prometheus exporter


- https://github.com/pimoroni/enviroplus-python
- https://github.com/prometheus/client_python

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
PM_SENSOR=True
LOCATION=default
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
