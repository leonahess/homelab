import logging
import os
import time
from prometheus_client import start_http_server, Summary, Gauge
from PyP100 import PyP110

########################################################################################################################
#                                                                                                                      #
# Logging configuration                                                                                                #
#                                                                                                                      #
########################################################################################################################

logging.basicConfig(
    format='%(asctime)s.%(msecs)03d %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

########################################################################################################################
#                                                                                                                      #
# Initialize Sensors                                                                                                   #
#                                                                                                                      #
########################################################################################################################

IP = os.getenv("IP", "default")
USERNAME = os.getenv("USERNAME", "default")
PASSWORD = os.getenv("PASSWORD", "default")

logging.info("Initializing Plug with IP: %s" % IP)
p110 = PyP110.P110(IP, USERNAME, PASSWORD)

########################################################################################################################
#                                                                                                                      #
# Stuff                                                                                            #
#                                                                                                                      #
########################################################################################################################


LOCATION = os.getenv("LOCATION", "default")
ROOM = os.getenv("ROOM", "default")
DEVICE = os.getenv("DEVICE", "default")
IS_LIGHT = os.getenv("IS_LIGHT", "default")
TYPE = os.getenv("TYPE", "default")

REQUEST_TIME = Summary('request_processing_seconds', 'Time spent processing request')

power = Gauge('smarthome_power_milliwatt', 'Power in milliwatt provided by the plug', ['location', 'room', 'device', 'is_light', 'type'])
energy_today = Gauge('smarthome_energy_today_watthours', 'Todays energy in watthours provided by the plug', ['location', 'room', 'device', 'is_light', 'type'])
energy_month = Gauge('smarthome_energy_month_watthours', 'This months energy in watthours provided by the plug', ['location', 'room', 'device', 'is_light', 'type'])
runtime_today = Gauge('smarthome_runtime_today_minutes', 'Todays runtime in minutes provided by the plug', ['location', 'room', 'device', 'is_light', 'type'])
runtime_month = Gauge('smarthome_runtime_month_minutes', 'Todays runtime in minutes provided by the plug', ['location', 'room', 'device', 'is_light', 'type'])

@REQUEST_TIME.time()
def process_request():
  response = p110.getEnergyUsage()
  logging.debug(response)

  power.labels(location=LOCATION, room=ROOM, device=DEVICE, is_light=IS_LIGHT, type=TYPE).set(response["current_power"])
  energy_today.labels(location=LOCATION, room=ROOM, device=DEVICE, is_light=IS_LIGHT, type=TYPE).set(response["today_energy"])
  energy_month.labels(location=LOCATION, room=ROOM, device=DEVICE, is_light=IS_LIGHT, type=TYPE).set(response["month_energy"])
  runtime_today.labels(location=LOCATION, room=ROOM, device=DEVICE, is_light=IS_LIGHT, type=TYPE).set(response["today_runtime"])
  runtime_month.labels(location=LOCATION, room=ROOM, device=DEVICE, is_light=IS_LIGHT, type=TYPE).set(response["month_runtime"])

if __name__ == '__main__':
    start_http_server(8000)

    while True:
        process_request()
        time.sleep(5)


