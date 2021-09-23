# -*- coding: utf-8 -*-
# (c) Copyright 2021 Sensirion AG, Switzerland

from __future__ import absolute_import, division, print_function

from sensirion_i2c_driver import I2cDevice

from .commands import Scd3XI2CCmdStartPeriodicMeasurement, \
    Scd3XI2CCmdReadMeasurement, Scd3XI2CCmdStopPeriodicMeasurement, \
    Scd3XI2CCmdSetTemperatureOffset, Scd3XI2CCmdSetAutomaticSelfCalibration, \
    Scd3XI2CCmdGetDataReadyStatus, Scd3XI2CCmdReinit, Scd3xI2cCmdGetTemperatureOffset


class Scd3xI2cDevice(I2cDevice):
    """
    SCD4x I²C device class to allow executing I²C commands.
    """

    def __init__(self, connection, slave_address=0x61):
        """
        Constructs a new SCD4X I²C device.

        :param ~sensirion_i2c_driver.connection.I2cConnection connection:
            The I²C connection to use for communication.
        :param byte slave_address:
            The I²C slave address, defaults to 0x62.
        """
        super(Scd3xI2cDevice, self).__init__(connection, slave_address)

    def start_periodic_measurement(self):
        """
        Start periodic measurement. Hard coded to run without pressure compensation.
        """

        result = self.execute(Scd3XI2CCmdStartPeriodicMeasurement())

        return result

    def read_measurement(self):
        """
        Read measurement during periodic measurement mode. Returns Co2, temperature and relative humidity
        as tuple

        :return:
            - co2 in ppm
            - temperature in celsius
            - humidity in %

        :rtype: tuple
        """
        return self.execute(Scd3XI2CCmdReadMeasurement())

    def stop_periodic_measurement(self):
        """
        Stop periodic measurement.

        .. note:: this command is only available in periodic measurement mode
        """
        return self.execute(Scd3XI2CCmdStopPeriodicMeasurement())

    def set_temperature_offset(self, t_offset):
        """
        Setting the temperature offset of the SCD4x
        inside the customer device correctly allows the user to leverage the RH and T
        output signal. Note that the temperature offset can depend on various factors
        such as the SCD4x measurement mode, self-heating of close components, the
        ambient temperature and air flow. Thus, the SCD4x temperature offset should
        be determined inside the customer device under its typical operation and in
        thermal equilibrium.

        .. note:: Only availabe in idle mode

        :param: (float) t_offset
                The temperature offset in degree Celsius
        """
        return self.execute(Scd3XI2CCmdSetTemperatureOffset(t_offset))

    def get_temperature_offset(self):
        """
        Get Temperature Offset I²C Command
        The temperature offset represents the difference between the measured
        temperature by the SCD4x and the actual ambient temperature. Per default,
        the temperature offset is set to 4°C.
        :return:
            - temperature (:py:class:`~sensirion_i2c_scd.scd4x.response_types.Scd4xTemperatureOffset`) -
              temperature offset response object
        .. note:: Only available in idle mode.
        """
        return self.execute(Scd3xI2cCmdGetTemperatureOffset())

    def set_automatic_self_calibration(self, asc_enabled):
        """
        Set Automatic Self Calibration I²C Command

        :param int asc_enabled:
            True to enable ASC, False to disable ASC
        """
        if asc_enabled:
            value = 1
        else:
            value = 0
        return self.execute(Scd3XI2CCmdSetAutomaticSelfCalibration(value))

    def get_data_ready_status(self):
        """
        Get Data Ready Status I²C Command

        Check whether new measurement data is available for read-out.

        :return: True if data ready, else False
        :rtype: bool
        """
        ret = self.execute(Scd3XI2CCmdGetDataReadyStatus())
        return (ret & 0x07FF) > 0

    def reinit(self):
        """
        Reinit I²C Command

        The reinit command reinitializes the sensor by reloading user settings from
        EEPROM. Before sending the reinit command, the stop measurement command
        must be issued. If reinit command does not trigger the desired
        re-initialization, a power-cycle should be applied to the SCD4x.

        .. note:: Only available in idle mode.
        """
        return self.execute(Scd3XI2CCmdReinit())
