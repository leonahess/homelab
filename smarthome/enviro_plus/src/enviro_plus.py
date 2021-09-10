import logging
import os
import socket
from dotenv import Dotenv
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS

import time

from bme280 import BME280
from pms5003 import PMS5003, ReadTimeoutError as pmsReadTimeoutError, SerialTimeoutError
from enviroplus import gas
try:
    # Transitional fix for breaking change in LTR559
    from ltr559 import LTR559
    ltr559 = LTR559()
except ImportError:
    import ltr559

dotenv = Dotenv(os.path.join(os.path.dirname(__file__), ".env"))
os.environ.update(dotenv)

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
# Influx configuration                                                                                                 #
#                                                                                                                      #
########################################################################################################################


bucket = os.getenv("INFLUX_BUCKET", "smarthome")
org = os.getenv("INFLUX_ORG", "me")
token = os.getenv("INFLUX_TOKEN")
url = os.getenv("INFLUX_URL", "https://influx.leona.pink:8086")

logging.info("Connecting to influx: %s" % url)

client = influxdb_client.InfluxDBClient(
    url=url,
    token=token,
    org=org
)
write_api = client.write_api(write_options=SYNCHRONOUS)

logging.info("Connected to influx: %s" % url)

########################################################################################################################
#                                                                                                                      #
# Initialize Sensors                                                                                                   #
#                                                                                                                      #
########################################################################################################################

# BME280 temperature/pressure/humidity sensor
logging.info("Initializing BME280 sensor")
bme280 = BME280()

# PMS5003 particulate sensor
pm_sensor = os.getenv("PM_SENSOR", False)
logging.info("Particle Sensor connected: %s" % pm_sensor)
if pm_sensor == True:
    logging.info("Initializing PMS5003 sensor")
    pms5003 = PMS5003()
    time.sleep(1.0)

########################################################################################################################
#                                                                                                                      #
# Stuff                                                                                            #
#                                                                                                                      #
########################################################################################################################

host = socket.gethostname()
location = os.getenv("TAG_LOCATION", "default")

# Create a values dict to store the data
variables = ["temperature",
             "pressure",
             "humidity",
             "light",
             "oxidised",
             "reduced",
             "nh3",
             "pm1",
             "pm25",
             "pm10"]

units = ["C",
         "hPa",
         "%",
         "Lux",
         "kO",
         "kO",
         "kO",
         "ug/m3",
         "ug/m3",
         "ug/m3"]

logging.info("Starting main loop")


def write_to_influx(measurement, field, field_data):
    point = influxdb_client.Point(measurement).tag("host", host).tag("location", location).field(field, field_data)
    write_api.write(bucket=bucket, org=org, record=point)


while True:
    proximity = ltr559.get_proximity()

    # Unit: C
    temp = bme280.get_temperature()
    write_to_influx("temperature", "temperature", float(temp))
    # Unit: %
    pressure = bme280.get_pressure()
    write_to_influx("pressure", "pressure", float(pressure))
    # Unit: hPa
    humidity = bme280.get_humidity()
    write_to_influx("humidity", "humidity", float(humidity))

    # Unit: Lux
    if proximity < 10:
        lux = ltr559.get_lux()
    else:
        lux = 1
    write_to_influx("light", "light", float(lux))

    # Unit: kOhm
    gas_data = gas.read_all()
    oxidising = gas_data.oxidising / 1000
    reducing = gas_data.reducing / 1000
    nh3 = gas_data.nh3 / 1000
    write_to_influx("gas", "oxidising", int(oxidising))
    write_to_influx("gas", "reducing", int(reducing))
    write_to_influx("gas", "nh3", int(nh3))

    # Unit: ug/m3
    if pm_sensor == True:
        pms_data = None
        try:
            pms_data = pms5003.read()
        except (SerialTimeoutError, pmsReadTimeoutError):
            logging.warning("Failed to read PMS5003")
        else:
            pm1 = float(pms_data.pm_ug_per_m3(1.0))
            pm2_5 = float(pms_data.pm_ug_per_m3(2.5))
            pm10 = float(pms_data.pm_ug_per_m3(10))
            write_to_influx("particulate_matter", "pm1", pm1)
            write_to_influx("particulate_matter", "pm2_5", pm2_5)
            write_to_influx("particulate_matter", "pm10", pm10)
