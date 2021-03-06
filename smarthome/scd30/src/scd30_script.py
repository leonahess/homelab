import time
import os
import socket
import logging

from dotenv import Dotenv
from sensirion_shdlc_driver import ShdlcSerialPort, ShdlcConnection
from sensirion_shdlc_sensorbridge import SensorBridgePort, \
    SensorBridgeShdlcDevice, SensorBridgeI2cProxy
from sensirion_i2c_driver import I2cConnection
from scd3x.device import Scd3xI2cDevice
from prometheus_client import start_http_server, Summary, Gauge

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
# Stuff                                                                                            #
#                                                                                                                      #
########################################################################################################################

LOCATION = os.getenv("LOCATION", "default")
ROOM = os.getenv("ROOM", "default")

REQUEST_TIME = Summary('request_processing_seconds', 'Time spent processing request')

tempe = Gauge('smarthome_temperature_celsius', 'Temperature in celsius provided by the sensor', ['location', 'room'])
gas = Gauge('smarthome_co2_ppm', 'CO2 concentration in ppm, provided by the sensor', ['location', 'room'])
hum = Gauge('smarthome_humidity_percent', 'Humidity in percents provided by the sensor', ['location', 'room'])


########################################################################################################################
#                                                                                                                      #
# Initialize Sensors                                                                                                   #
#                                                                                                                      #
########################################################################################################################


@REQUEST_TIME.time()
def continuous_reading(scd30: Scd3xI2cDevice):
    while True:
        logging.debug("Data ready: {}".format(scd30.get_data_ready_status()))
        if scd30.get_data_ready_status():
            logging.debug("Reading from sensor.")
            measurement = scd30.read_measurement()
            logging.debug("Read from sensor.")
            logging.debug("Measurement: {}".format(measurement))
            if measurement is not None:
                co2, temp, rh = measurement
                logging.debug(f"CO2: {co2:.2f}ppm, temp: {temp:.2f}'C, rh: {rh:.2f}%")
                gas.labels(location=LOCATION, room=ROOM).set(float(co2))
                tempe.labels(location=LOCATION, room=ROOM).set(float(temp))
                hum.labels(location=LOCATION, room=ROOM).set(float(rh))
            time.sleep(measurement_interval)
        else:
            time.sleep(0.2)
        time.sleep(1)


logging.info("Starting main loop")

# Connect to the SensorBridge with default settings:
#  - baudrate:      460800
#  - slave address: 0
with ShdlcSerialPort(port='/dev/ttyUSB0', baudrate=460800) as port:
    bridge = SensorBridgeShdlcDevice(ShdlcConnection(port), slave_address=0)
    logging.info("SensorBridge SN: {}".format(bridge.get_serial_number()))

    # Configure SensorBridge port 1 for SCD4x
    bridge.set_i2c_frequency(SensorBridgePort.ONE, frequency=100e3)
    bridge.set_supply_voltage(SensorBridgePort.ONE, voltage=3.6)
    bridge.switch_supply_on(SensorBridgePort.ONE)

    # Create SCD41 device
    i2c_transceiver = SensorBridgeI2cProxy(bridge, port=SensorBridgePort.ONE)
    scd30 = Scd3xI2cDevice(I2cConnection(i2c_transceiver))

    retries = 30
    logging.info("Probing sensor...")
    ready = None
    while ready is None and retries:
        try:
            ready = scd30.get_data_ready_status()
        except OSError:
            # The sensor may need a couple of seconds to boot up after power-on
            # and may not be ready to respond, raising I2C errors during this time.
            pass
        time.sleep(1)
        retries -= 1
    if not retries:
        logging.error("Timed out waiting for SCD30.")
        exit(1)

    logging.info("Link to sensor established.")


    # 2 seconds is the minimum supported interval.
    temp_offset = 2 * 100
    current_temp_offset = scd30.get_temperature_offset()
    measurement_interval = 2
    #logging.info("Setting measurement interval to 2s...")
    #scd30.set_measurement_interval(measurement_interval)

    logging.info("Getting temp offset: {} celsius".format(current_temp_offset))
    if temp_offset != (current_temp_offset * 100):
        logging.info("Setting temp offset interval to {} celsius...".format(temp_offset / 100))
        scd30.set_temperature_offset(temp_offset)
        logging.info("Getting temp offset: {}".format(scd30.get_temperature_offset()))
    logging.info("Enabling automatic self-calibration...")
    scd30.set_automatic_self_calibration(True)
    logging.info("Starting periodic measurement...")
    scd30.start_periodic_measurement()

    time.sleep(measurement_interval)

    start_http_server(8001)
    try:
        continuous_reading(scd30)
    except KeyboardInterrupt:
        logging.info("Stopping periodic measurement...")
        scd30.stop_periodic_measurement()
