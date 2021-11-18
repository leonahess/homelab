import logging
import os
from dotenv import Dotenv
from prometheus_client import start_http_server, Summary, Gauge

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
# Initialize Sensors                                                                                                   #
#                                                                                                                      #
########################################################################################################################

# BME280 temperature/pressure/humidity sensor
logging.info("Initializing BME280 sensor")
bme280 = BME280()

# PMS5003 particulate sensor
pm_sensor = os.getenv("PM_SENSOR", "False")
logging.info("Particle Sensor connected: %s" % pm_sensor)
if pm_sensor == "True":
    logging.info("Initializing PMS5003 sensor")
    pms5003 = PMS5003()
    time.sleep(1.0)

########################################################################################################################
#                                                                                                                      #
# Stuff                                                                                            #
#                                                                                                                      #
########################################################################################################################

REQUEST_TIME = Summary('request_processing_seconds', 'Time spent processing request')

temp = Gauge('smarthome_temperature_celsius', 'Temperature in celsius provided by the sensor')
hum = Gauge('smarthome_humidity_percent', 'Humidity in percents provided by the sensor')
pres = Gauge('smarthome_pressure_hectopascal', 'Pressure in percents provided by the sensor')
lux = Gauge('smarthome_illuminance_lux', 'Illuminance in lux provided by the sensor')

oxidising = Gauge('smarthome_resistance_oxidising_kiloohm', 'Oxidising gas resistance in kiloohm')
reducing = Gauge('smarthome_resistance_reducing_kiloohm', 'Reducing gas resistance in kiloohm')
nh3 = Gauge('smarthome_resistance_nh3_kiloohm', 'NH3 gas resistance in kiloohm')

pm1 = Gauge('smarthome_particulate_matter_1_microgram_per_cubic_meter', 'PM1 particulate matter in microgram per cubic meter')
pm2_5 = Gauge('smarthome_particulate_matter_2_5_microgram_per_cubic_meter', 'PM2,5 particulate matter in microgram per cubic meter')
pm10 = Gauge('smarthome_particulate_matter_10_microgram_per_cubic_meter', 'PM10 particulate matter in microgram per cubic meter')

l003 = Gauge('smarthome_particles_per_300_nanometer_per_deciliter', '300 nanometer sized Particles in the air per deciliter')
l005 = Gauge('smarthome_particles_per_500_nanometer_per_deciliter', '500 nanometer sized Particles in the air per deciliter')
l010 = Gauge('smarthome_particles_per_1000_nanometer_per_deciliter', '1000 nanometer sized Particles in the air per deciliter')
l025 = Gauge('smarthome_particles_per_2500_nanometer_per_deciliter', '2500 nanometer sized Particles in the air per deciliter')
l050 = Gauge('smarthome_particles_per_5000_nanometer_per_deciliter', '5000 nanometer sized Particles in the air per deciliter')
l100 = Gauge('smarthome_particles_per_10000_nanometer_per_deciliter', '10000 nanometer sized Particles in the air per deciliter')


@REQUEST_TIME.time()
def process_request():
    proximity = ltr559.get_proximity()

    # Unit: C
    temp.set(float(bme280.get_temperature()))
    # Unit: %
    pres.set(float(bme280.get_pressure()))
    # Unit: hPa
    hum.set(float(bme280.get_humidity()))

    # Unit: Lux
    if proximity < 10:
        lux.set(ltr559.get_lux())
    else:
        lux.set(1)

    # Unit: kOhm
    gas_data = gas.read_all()
    oxidising.set(gas_data.oxidising / 1000)
    reducing.set(gas_data.reducing / 1000)
    nh3.set(gas_data.nh3 / 1000)

    # Unit: ug/m3
    if pm_sensor == "True":
        pms_data = None
        try:
            pms_data = pms5003.read()
        except (SerialTimeoutError, pmsReadTimeoutError):
            logging.warning("Failed to read PMS5003")
        else:
            pm1.set(float(pms_data.pm_ug_per_m3(1.0)))
            pm2_5.set(float(pms_data.pm_ug_per_m3(2.5)))
            pm10.set(float(pms_data.pm_ug_per_m3(10)))

            l003.set(float(pms_data.pm_per_1l_air(0.3)))
            l005.set(float(pms_data.pm_per_1l_air(0.5)))
            l010.set(float(pms_data.pm_per_1l_air(1.0)))
            l025.set(float(pms_data.pm_per_1l_air(2.5)))
            l050.set(float(pms_data.pm_per_1l_air(5)))
            l100.set(float(pms_data.pm_per_1l_air(10)))


if __name__ == '__main__':
    start_http_server(8000)

    while True:
        process_request()
        time.sleep(1)


