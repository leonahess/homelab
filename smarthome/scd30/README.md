# Script to read Sensirio's SCD30 CO2 sensor and expose prometheus exporter

The Sensor is connected to sensirios Sensor Bridge, which is connected to a Raspberry Pi. In `./src/scd3x` I have adapted 
Sensirio's [SCD4x python driver](https://github.com/Sensirion/python-i2c-scd) to work with the SCD30. There was
an [existing SCD30 driver](https://github.com/RequestForCoffee/scd30) but that doesn't work with the Sensor Bridge.

- https://www.sensirion.com/en/environmental-sensors/carbon-dioxide-sensors/carbon-dioxide-sensors-scd30/
- https://sensirion.github.io/python-i2c-scd/index.html
- https://sensirion.github.io/python-shdlc-driver/index.html
- https://sensirion.github.io/python-i2c-driver/index.html
- https://sensirion.github.io/python-shdlc-sensorbridge/index.html
- https://github.com/prometheus/client_python

## Setup the Pi

```
sudo apt update && sudo apt upgrade -y
cd ~
git clone https://github.com/leonahess/homelab.git
```

You might have to do some tricks to get the Sensor Bridge to show up as a serial device (`ttyUSB0`). See here for info: https://unix.stackexchange.com/questions/67936/attaching-usb-serial-device-with-custom-pid-to-ttyusb0-on-embedded/165845

Use `dmesg | grep usb` to find the Vendor id and Product id of the Sensor Bridge.

1. Add the following single line to `/etc/udev/rules.d/99-ftdi.rules`
```
ACTION=="add", ATTRS{idVendor}=="0403", ATTRS{idProduct}=="7168", RUN+="/sbin/modprobe ftdi_sio" RUN+="/bin/sh -c 'echo 0403 7168 > /sys/bus/usb-serial/drivers/ftdi_sio/new_id'"
```
2. Either reboot or run `sudo udevadm control --reload` to pick up the new rule.
3. Unplug the device.
4. Plug in the device.

## Setup the script

Create .env file in /home/pi/homelab/smarthome/scd30/src
```
nano /home/pi/homelab/smarthome/scd30/src/.env
```

.env file:
```
LOCATION=default
```

Install python modules
```
pip3 install -r requirements.txt
```

Move service to /etc/systemd/system and start it
```
sudo cp /home/pi/homelab/smarthome/scd30/scd30.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable scd30.service
sudo systemctl start scd30.service
```
