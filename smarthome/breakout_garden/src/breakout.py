import logging
import os
import socket
from dotenv import Dotenv
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
import bme680
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


def write_to_influx(measurement, field, field_data, location_data):
    point = influxdb_client.Point(measurement).tag("host", host).tag("location", location_data).field(field, field_data)
    write_api.write(bucket=bucket, org=org, record=point)


logging.info("Starting main loop")
while True:
    if bme688_sensor_primary == "1":
        if sensor1.get_sensor_data():
            write_to_influx("temperature", "temperature", float(sensor1.data.temperature), bme688_sensor_primary_location)
            write_to_influx("pressure", "pressure", float(sensor1.data.pressure), bme688_sensor_primary_location)
            write_to_influx("humidity", "humidity", float(sensor1.data.humidity), bme688_sensor_primary_location)

    if bme688_sensor_secondary == "1":
        if sensor2.get_sensor_data():
            write_to_influx("temperature", "temperature", float(sensor2.data.temperature), bme688_sensor_secondary_location)
            write_to_influx("pressure", "pressure", float(sensor2.data.pressure), bme688_sensor_secondary_location)
            write_to_influx("humidity", "humidity", float(sensor2.data.humidity), bme688_sensor_secondary_location)

    if sgp30_sensor == "1":
        res = sgp30.get_air_quality()
        write_to_influx("gas", "eco2", int(res.equivalent_co2), sgp30_sensor_location)
        write_to_influx("gas", "tvoc", int(res.total_voc), sgp30_sensor_location)
