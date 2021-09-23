# -*- coding: utf-8 -*-
# (c) Copyright 2021 Sensirion AG, Switzerland

# flake8: noqa

from __future__ import absolute_import, division, print_function

from struct import pack, unpack

from sensirion_i2c_driver import SensirionI2cCommand, CrcCalculator

import logging
import struct


def interpret_as_float(integer: int):
    return struct.unpack('!f', struct.pack('!I', integer))[0]


class Scd3xI2cCmdBase(SensirionI2cCommand):
    """
    SCD4x I²C base command.
    """

    def __init__(self, command, tx_data, rx_length, read_delay, timeout,
                 post_processing_time=0.0):
        """
        Constructs a new SCD4x I²C command.

        :param int/None command:
            The command ID to be sent to the device. None means that no
            command will be sent, i.e. only ``tx_data`` (if not None) will
            be sent. No CRC is added to these bytes since the command ID
            usually already contains a CRC.
        :param bytes-like/list/None tx_data:
            Bytes to be extended with CRCs and then sent to the I²C device.
            None means that no write header will be sent at all (if ``command``
            is None too). An empty list means to send the write header (even if
            ``command`` is None), but without data following it.
        :param int/None rx_length:
            Number of bytes to be read from the I²C device, including CRC
            bytes. None means that no read header is sent at all. Zero means
            to send the read header, but without reading any data.
        :param float read_delay:
            Delay (in Seconds) to be inserted between the end of the write
            operation and the beginning of the read operation. This is needed
            if the device needs some time to prepare the RX data, e.g. if it
            has to perform a measurement. Set to 0.0 to indicate that no delay
            is needed, i.e. the device does not need any processing time.
        :param float timeout:
            Timeout (in Seconds) to be used in case of clock stretching. If the
            device stretches the clock longer than this value, the transceive
            operation will be aborted with a timeout error. Set to 0.0 to
            indicate that the device will not stretch the clock for this
            command.
        :param float post_processing_time:
            Maximum time in seconds the device needs for post processing of
            this command until it is ready to receive the next command. For
            example after a device reset command, the device might need some
            time until it is ready again. Usually this is 0.0s, i.e. no post
            processing is needed.
        """
        super(Scd3xI2cCmdBase, self).__init__(
            command=command,
            tx_data=tx_data,
            rx_length=rx_length,
            read_delay=read_delay,
            timeout=timeout,
            crc=CrcCalculator(8, 0x31, 0xFF, 0x00),
            command_bytes=2,
            post_processing_time=post_processing_time,
        )


class Scd3XI2CCmdStartPeriodicMeasurement(Scd3xI2cCmdBase):
    """
    Start Periodic Measurement I²C Command

    start periodic measurement, signal update interval is 5 seconds.

    .. note:: This command is only available in idle mode.
    """

    def __init__(self):
        """
        Constructor.
        """
        super(Scd3XI2CCmdStartPeriodicMeasurement, self).__init__(
            command=0x0010,
            tx_data=b"".join([pack(">H", 0)]),
            rx_length=None,
            read_delay=0.0,
            timeout=0.05,
            post_processing_time=0.001,
        )


class Scd3XI2CCmdReadMeasurement(Scd3xI2cCmdBase):
    """
    Read Measurement I²C Command

    read sensor output. The measurement data can only be read out once per
    signal update interval as the buffer is emptied upon read-out. If no data
    is available in the buffer, the sensor returns a NACK. To avoid a NACK
    response the get_data_ready_status can be issued to check data status. The
    I2C master can abort the read transfer with a NACK followed by a STOP
    condition after any data byte if the user is not interested in subsequent
    data.

    .. note:: This command is only available in measurement mode. The firmware
              updates the measurement values depending on the measurement mode.
    """

    def __init__(self):
        """
        Constructor.
        """
        super(Scd3XI2CCmdReadMeasurement, self).__init__(
            command=0x0300,
            tx_data=None,
            rx_length=18,
            read_delay=0.001,
            timeout=0.05,
            post_processing_time=0.0,
        )

    def interpret_response(self, data):
        """
        Validates the CRCs of the received data from the device and returns
        the interpreted data.

        :param bytes data:
            Received raw bytes from the read operation.
        :return:
            - co2 (:py:class:`~sensirion_i2c_scd.scd4x.response_types.Scd4xCarbonDioxid`) -
              CO₂ response object
            - temperature (:py:class:`~sensirion_i2c_scd.scd4x.response_types.Scd4xTemperature`) -
              Temperature response object.
            - humidity (:py:class:`~sensirion_i2c_scd.scd4x.response_types.Scd4xHumidity`) -
              Humidity response object
        :rtype: tuple
        :raise ~sensirion_i2c_driver.errors.I2cChecksumError:
            If a received CRC was wrong.
        """
        # check and remove CRCs
        logging.debug("data: {}".format(data))
        checked_data = Scd3xI2cCmdBase.interpret_response(self, data)
        logging.debug("checked data: {}".format(checked_data))

        # convert raw received data into proper data types
        final_data = [int.from_bytes(checked_data[:2], "big"), int.from_bytes(checked_data[2:4], "big"), int.from_bytes(checked_data[4:6], "big"), int.from_bytes(checked_data[6:8], "big"), int.from_bytes(checked_data[8:10], "big"), int.from_bytes(checked_data[10:], "big")]

        co2  = interpret_as_float((final_data[0] << 16) | final_data[1])
        temp = interpret_as_float((final_data[2] << 16) | final_data[3])
        hum  = interpret_as_float((final_data[4] << 16) | final_data[5])
        logging.debug("co2: {}, temp: {}, hum:{}".format(co2, temp, hum))

        return co2, temp, hum


class Scd3XI2CCmdStopPeriodicMeasurement(Scd3xI2cCmdBase):
    """
    Stop Periodic Measurement I²C Command

    Stop periodic measurement and return to idle mode for sensor configuration
    or to safe energy.

    .. note:: This command is only available in measurement mode.
    """

    def __init__(self):
        """
        Constructor.
        """
        super(Scd3XI2CCmdStopPeriodicMeasurement, self).__init__(
            command=0x0104,
            tx_data=None,
            rx_length=None,
            read_delay=0.0,
            timeout=0.05,
            post_processing_time=0.5,
        )


class Scd3XI2CCmdSetTemperatureOffset(Scd3xI2cCmdBase):
    """
    Set Temperature Offset I²C Command

    Setting the temperature offset of the SCD4x inside the customer device
    correctly allows the user to leverage the RH and T output signal. Note that
    the temperature offset can depend on various factors such as the SCD4x
    measurement mode, self-heating of close components, the ambient temperature
    and air flow. Thus, the SCD4x temperature offset should be determined
    inside the customer device under its typical operation and in thermal
    equilibrium.

    .. note:: Only available in idle mode.
    """

    def __init__(self, t_offset):
        """
        Constructor.

        :param int t_offset:
            Temperature offset in degree celsius
        """

        super(Scd3XI2CCmdSetTemperatureOffset, self).__init__(
            command=0x5403,
            tx_data=b"".join([pack(">H", t_offset)]),
            rx_length=None,
            read_delay=0.0,
            timeout=0.05,
            post_processing_time=0.001,
        )


class Scd3xI2cCmdGetTemperatureOffset(Scd3xI2cCmdBase):
    """
    Get Temperature Offset I²C Command
    The temperature offset represents the difference between the measured
    temperature by the SCD4x and the actual ambient temperature. Per default,
    the temperature offset is set to 4°C.
    .. note:: Only available in idle mode.
    """

    def __init__(self):
        """
        Constructor.
        """
        super(Scd3xI2cCmdGetTemperatureOffset, self).__init__(
            command=0x5403,
            tx_data=None,
            rx_length=3,
            read_delay=0.001,
            timeout=0,
            post_processing_time=0.0,
        )

    def interpret_response(self, data):
        """
        Validates the CRCs of the received data from the device and returns
        the interpreted data.
        :param bytes data:
            Received raw bytes from the read operation.
        :return:
            - temperature offset (:py:class:`~sensirion_i2c_scd.scd4x.response_types.Scd4xTemperatureOffset`) -
              TemperatureOffset response object.
        :raise ~sensirion_i2c_driver.errors.I2cChecksumError:
            If a received CRC was wrong.
        """
        # check and remove CRCs
        checked_data = Scd3xI2cCmdBase.interpret_response(self, data)

        # convert raw received data into proper data types
        return int.from_bytes(checked_data[:2], "big") / 100


class Scd3XI2CCmdSetAutomaticSelfCalibration(Scd3xI2cCmdBase):
    """
    Set Automatic Self Calibration I²C Command

    By default, the ASC is enabled.
    """

    def __init__(self, asc_enabled):
        """
        Constructor.

        :param int asc_enabled:
            1 to enable ASC, 0 to disable ASC
        """
        super(Scd3XI2CCmdSetAutomaticSelfCalibration, self).__init__(
            command=0x5306,
            tx_data=b"".join([pack(">H", asc_enabled)]),
            rx_length=None,
            read_delay=0.0,
            timeout=0.05,
            post_processing_time=0.001,
        )


class Scd3XI2CCmdGetDataReadyStatus(Scd3xI2cCmdBase):
    """
    Get Data Ready Status I²C Command

    Check whether new measurement data is available for read-out.
    """

    def __init__(self):
        """
        Constructor.
        """
        super(Scd3XI2CCmdGetDataReadyStatus, self).__init__(
            command=0x0202,
            tx_data=None,
            rx_length=3,
            read_delay=0.001,
            timeout=0.05,
            post_processing_time=0.0,
        )

    def interpret_response(self, data):
        """
        Validates the CRCs of the received data from the device and returns
        the interpreted data.

        :param bytes data:
            Received raw bytes from the read operation.
        :return: If last 11 bits are 0 data not ready, else data ready
        :rtype: int
        :raise ~sensirion_i2c_driver.errors.I2cChecksumError:
            If a received CRC was wrong.
        """
        # check and remove CRCs
        checked_data = Scd3xI2cCmdBase.interpret_response(self, data)

        # convert raw received data into proper data types
        data_ready = int(unpack(">H", checked_data[0:2])[0])  # uint16
        return data_ready


class Scd3XI2CCmdReinit(Scd3xI2cCmdBase):
    """
    Reinit I²C Command

    The reinit command reinitializes the sensor by reloading user settings from
    EEPROM. Before sending the reinit command, the stop measurement command
    must be issued. If reinit command does not trigger the desired
    re-initialization, a power-cycle should be applied to the SCD4x.

    .. note:: Only available in idle mode.
    """

    def __init__(self):
        """
        Constructor.
        """
        super(Scd3XI2CCmdReinit, self).__init__(
            command=0xD304,
            tx_data=None,
            rx_length=None,
            read_delay=0.0,
            timeout=0.05,
            post_processing_time=0.02,
        )
