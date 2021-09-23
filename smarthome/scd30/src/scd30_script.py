import time, logging
from sensirion_shdlc_driver import ShdlcSerialPort, ShdlcConnection
from sensirion_shdlc_sensorbridge import SensorBridgePort, \
    SensorBridgeShdlcDevice, SensorBridgeI2cProxy
from sensirion_i2c_driver import I2cConnection

from scd3x.device import Scd3xI2cDevice


def continuous_reading(scd30: Scd3xI2cDevice):
    while True:
        logging.debug("Data ready: {}".format(scd30.get_data_ready_status()))
        if scd30.get_data_ready_status():
            logging.debug("Reading from sensor.")
            measurement = scd30.read_measurement()
            logging.debug("Read from sensor.")
            logging.debug("Measurement: {}".format(measurement))
            #logging.info("Co2: {}, temp: {}, rh: {}".format(measurement[0].co2, measurement[1].degrees_celsius, measurement[2].percent_rh))
            if measurement is not None:
                co2, temp, rh = measurement
                print(f"CO2: {co2:.2f}ppm, temp: {temp:.2f}'C, rh: {rh:.2f}%")
            time.sleep(measurement_interval)
        else:
            time.sleep(0.2)


# Connect to the SensorBridge with default settings:
#  - baudrate:      460800
#  - slave address: 0
with ShdlcSerialPort(port='/dev/ttyUSB0', baudrate=460800) as port:
    bridge = SensorBridgeShdlcDevice(ShdlcConnection(port), slave_address=0)
    print("SensorBridge SN: {}".format(bridge.get_serial_number()))

    # Configure SensorBridge port 1 for SCD4x
    bridge.set_i2c_frequency(SensorBridgePort.ONE, frequency=100e3)
    bridge.set_supply_voltage(SensorBridgePort.ONE, voltage=3.6)
    bridge.switch_supply_on(SensorBridgePort.ONE)

    # Create SCD41 device
    i2c_transceiver = SensorBridgeI2cProxy(bridge, port=SensorBridgePort.ONE)
    scd30 = Scd3xI2cDevice(I2cConnection(i2c_transceiver))

    logging.basicConfig(level=logging.INFO)

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
    measurement_interval = 2
    #logging.info("Setting measurement interval to 2s...")
    #scd30.set_measurement_interval(measurement_interval)
    logging.info("Getting temp offset...")
    scd30.get_temperature_offset()
    logging.info("Setting temp offset interval to 2 C...")
    scd30.set_temperature_offset(2.0)
    logging.info("Enabling automatic self-calibration...")
    scd30.set_automatic_self_calibration(True)
    logging.info("Starting periodic measurement...")
    scd30.start_periodic_measurement()

    time.sleep(measurement_interval)

    try:
        continuous_reading(scd30)
    except KeyboardInterrupt:
        logging.info("Stopping periodic measurement...")
        scd30.stop_periodic_measurement()
