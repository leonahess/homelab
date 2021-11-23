import logging
import os
import socket
import time
import bme680

from dotenv import Dotenv
from prometheus_client import start_http_server, Summary, Gauge
from sgp30 import SGP30


########################################################################################################################
#                                                                                                                      #
# Load .env file and load ENVs                                                                                         #
#                                                                                                                      #
########################################################################################################################

dotenv = Dotenv(os.path.join(os.path.dirname(__file__), ".env"))
os.environ.update(dotenv)

host = socket.gethostname()

sgp30_sensor = os.getenv("SGP30_SENSOR", "0")
VEML6075_sensor = os.getenv("VEML6075_SENSOR", "0")
bme688_sensor_primary = os.getenv("BME688_SENSOR_PRIMARY", "0")
bme688_sensor_secondary = os.getenv("BME688_SENSOR_SECONDARY", "0")

sgp30_sensor_location = os.getenv("SGP30_SENSOR_TAG_LOCATION", "default")
VEML6075_sensor_location = os.getenv("VEML6075_SENSOR_TAG_LOCATION", "default")
bme688_sensor_primary_location = os.getenv("BME688_SENSOR_PRIMARY_TAG_LOCATION", "default")
bme688_sensor_secondary_location = os.getenv("BME688_SENSOR_SECONDARY_TAG_LOCATION", "default")

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

logging.info("Primary BME688 connected: %s" % bme688_sensor_primary)
if bme688_sensor_primary == "1":
    logging.info("Initializing first BME688 sensor")
    sensor1 = bme680.BME680(bme680.I2C_ADDR_PRIMARY)

    logging.info("Setting oversampling for first BME688 sensor")
    sensor1.set_humidity_oversample(bme680.OS_2X)
    sensor1.set_pressure_oversample(bme680.OS_4X)
    sensor1.set_temperature_oversample(bme680.OS_8X)
    sensor1.set_filter(bme680.FILTER_SIZE_3)

logging.info("Secondary BME688 connected: %s" % bme688_sensor_secondary)
if bme688_sensor_secondary == "1":
    logging.info("Initializing second BME688 sensor")
    sensor2 = bme680.BME680(bme680.I2C_ADDR_SECONDARY)

    logging.info("Setting oversampling for second BME688 sensor")
    sensor2.set_humidity_oversample(bme680.OS_2X)
    sensor2.set_pressure_oversample(bme680.OS_4X)
    sensor2.set_temperature_oversample(bme680.OS_8X)
    sensor2.set_filter(bme680.FILTER_SIZE_3)

logging.info("SGP30 connected: %s" % sgp30_sensor)
if sgp30_sensor == "1":
    logging.info("Initializing SGP30 sensor")
    sgp30 = SGP30()

    logging.info("Warming up sensor...")
    sgp30.start_measurement()

########################################################################################################################
#                                                                                                                      #
# Stuff                                                                                                                #
#                                                                                                                      #
########################################################################################################################

LOCATION1 = os.getenv("BME688_SENSOR_PRIMARY_TAG_LOCATION", "default")
LOCATION2 = os.getenv("BME688_SENSOR_SECONDARY_TAG_LOCATION", "default")
SGP_LOCATION = os.getenv("SGP30_SENSOR_TAG_LOCATION", "default")

REQUEST_TIME = Summary('request_processing_seconds', 'Time spent processing request')

temp = Gauge('smarthome_temperature_celsius', 'Temperature in celsius provided by the sensor', ['location'])
pressure = Gauge('smarthome_pressure_hectopascal', 'Pressure in percents provided by the sensor', ['location'])
hum = Gauge('smarthome_humidity_percent', 'Humidity in percents provided by the sensor', ['location'])
eco2 = Gauge('smarthome_eco2_ppm', 'equivalent CO2 concentration in ppm, provided by the sensor', ['location'])
tvoc = Gauge('smarthome_tvoc_ppb', 'TVOC concentration in ppb, provided by the sensor', ['location'])


@REQUEST_TIME.time()
def process_request():
    if bme688_sensor_primary == "1":
        if sensor1.get_sensor_data():
            temp.labels(location=LOCATION1).set(float(sensor1.data.temperature))
            pressure.labels(location=LOCATION1).set(float(sensor1.data.pressure))
            hum.labels(locatin=LOCATION1).set(float(sensor1.data.humidity))

    if bme688_sensor_secondary == "1":
        if sensor2.get_sensor_data():
            temp.labels(location=LOCATION2).set(float(sensor1.data.temperature))
            pressure.labels(location=LOCATION2).set(float(sensor1.data.pressure))
            hum.labels(location=LOCATION2).set(float(sensor1.data.humidity))

    if sgp30_sensor == "1":
        res = sgp30.get_air_quality()
        eco2.labels(location=SGP_LOCATION).set(int(res.equivalent_co2))
        tvoc.labels(location=SGP_LOCATION).set(int(res.total_voc))


logging.info("Starting main loop")

start_http_server(8003)
while True:
    process_request()
    time.sleep(1)
