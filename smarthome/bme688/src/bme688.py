import logging
import os
import socket
from dotenv import Dotenv
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
import bme680
import time

########################################################################################################################
#                                                                                                                      #
# Load .env file                                                                                                #
#                                                                                                                      #
########################################################################################################################

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

logging.info("Initializing first BME688 sensor")
sensor1 = bme680.BME680(bme680.I2C_ADDR_PRIMARY)
logging.info("Initializing second BME688 sensor")
sensor2 = bme680.BME680(bme680.I2C_ADDR_SECONDARY)

logging.info("Setting oversampling for first BME688 sensor")
sensor1.set_humidity_oversample(bme680.OS_2X)
sensor1.set_pressure_oversample(bme680.OS_4X)
sensor1.set_temperature_oversample(bme680.OS_8X)
sensor1.set_filter(bme680.FILTER_SIZE_3)

logging.info("Setting oversampling for second BME688 sensor")
sensor2.set_humidity_oversample(bme680.OS_2X)
sensor2.set_pressure_oversample(bme680.OS_4X)
sensor2.set_temperature_oversample(bme680.OS_8X)
sensor2.set_filter(bme680.FILTER_SIZE_3)

sensor2.set_gas_heater_temperature(320)
sensor2.set_gas_heater_duration(150)
sensor2.select_gas_heater_profile(0)

start_time = time.time()
curr_time = time.time()
burn_in_time = 300

burn_in_data = []

########################################################################################################################
#                                                                                                                      #
# Stuff                                                                                            #
#                                                                                                                      #
########################################################################################################################

host = socket.gethostname()
location = os.getenv("TAG_LOCATION", "default")

logging.info("Starting main loop")


def write_to_influx(measurement, field, field_data, sensor):
    point = influxdb_client.Point(measurement).tag("host", host).tag("location", location).tag("sensor", sensor).field(field, field_data)
    write_api.write(bucket=bucket, org=org, record=point)


logging.info("Collecting gas resistance burn-in data for 5 mins")
while curr_time - start_time < burn_in_time:
    curr_time = time.time()
    if sensor2.get_sensor_data() and sensor2.data.heat_stable:
        gas = sensor2.data.gas_resistance
        burn_in_data.append(gas)
        logging.info("Gas: {0} Ohms".format(gas))
        time.sleep(1)

gas_baseline = sum(burn_in_data[-50:]) / 50.0

# Set the humidity baseline to 40%, an optimal indoor humidity.
hum_baseline = 40.0

# This sets the balance between humidity and gas reading in the
# calculation of air_quality_score (25:75, humidity:gas)
hum_weighting = 0.25

while True:
    if sensor1.get_sensor_data():
        write_to_influx("temperature", "temperature", float(sensor1.data.temperature),1)
        write_to_influx("pressure", "pressure", float(sensor1.data.pressure), 1)
        write_to_influx("humidity", "humidity", float(sensor1.data.humidity), 1)

    if sensor2.get_sensor_data():
        write_to_influx("temperature", "temperature", float(sensor2.data.temperature), 2)
        write_to_influx("pressure", "pressure", float(sensor2.data.pressure), 2)
        write_to_influx("humidity", "humidity", float(sensor2.data.humidity), 2)

    if sensor2.get_sensor_data() and sensor2.data.heat_stable:
        gas = sensor2.data.gas_resistance
        gas_offset = gas_baseline - gas

        hum = sensor2.data.humidity
        hum_offset = hum - hum_baseline

        # Calculate hum_score as the distance from the hum_baseline.
        if hum_offset > 0:
            hum_score = (100 - hum_baseline - hum_offset)
            hum_score /= (100 - hum_baseline)
            hum_score *= (hum_weighting * 100)

        else:
            hum_score = (hum_baseline + hum_offset)
            hum_score /= hum_baseline
            hum_score *= (hum_weighting * 100)

        # Calculate gas_score as the distance from the gas_baseline.
        if gas_offset > 0:
            gas_score = (gas / gas_baseline)
            gas_score *= (100 - (hum_weighting * 100))

        else:
            gas_score = 100 - (hum_weighting * 100)

        # Calculate air_quality_score.
        air_quality_score = hum_score + gas_score
        write_to_influx("Air Quality Index", "AQI", float(air_quality_score), 2)

        time.sleep(1)

