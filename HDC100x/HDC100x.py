#!/usr/bin/env python
#
# File: $Id$
#
"""
Class to read from the HDC100X sensor over I2C on a Raspberry Pi

To setup for reading:

>>> from HDC100x import HDC100x
>>> hdc = HDC100x()
>>> temp, humid = hdc.data()
"""

# system imports
#
import time

# 3rd party imports
#
from Adafruit_GPIO import I2C

# Constants
#
HDC100X_I2CADDR = 0x40  # standard default i2c address for the sensor
HDC1000_TEMP = 0x00
HDC1000_HUMID = 0x01
HDC1000_CONFIG = 0x02
HDC1000_CONFIG_RST = (1 << 15)
HDC1000_CONFIG_HEAT = (1 << 13)
HDC1000_CONFIG_MODE = (1 << 12)
HDC1000_CONFIG_BATT = (1 << 11)
HDC1000_CONFIG_TRES_14 = 0
HDC1000_CONFIG_TRES_11 = (1 << 10)
HDC1000_CONFIG_HRES_14 = 0
HDC1000_CONFIG_HRES_11 = (1 << 8)
HDC1000_CONFIG_HRES_8 = (1 << 9)

HDC1000_SERIAL1 = 0xFB
HDC1000_SERIAL2 = 0xFC
HDC1000_SERIAL3 = 0xFD
HDC1000_MANUFID = 0xFE
HDC1000_DEVICEID = 0xFF


########################################################################
########################################################################
#
class HDC100x(object):
    """
    Class to read from the HDC100X sensor over I2C on a Raspberry Pi

    To setup for reading:

    >>> from HDC100x import HDC100x
    >>> hdc = HDC100x()
    >>> temp, humid = hdc.data()
    """

    ####################################################################
    #
    def __init__(self, address=HDC100X_I2CADDR,  i2c_bus=None, **kwargs):
        """
        By default assumes the default I2C address.  If no I2C module is
        passed in it will use the default I2C bus on the host it is
        running on.
        """
        # Create I2C device. If we were not passed a specific I2C bus
        # then use the default one. Do not like the in-line
        # imports. Adafruit coders need a solid dose of PEP8
        #
        if i2c_bus is None:
            i2c_bus = I2C
        self._device = i2c_bus.get_i2c_device(address, **kwargs)
        self.reset()

        manuf_id = self._device.readU16BE(HDC1000_MANUFID)
        if manuf_id != 0x5449:
            raise RuntimeError("Device at '%x' has an unexpected "
                               "manufacturers id '%x' (Expected %x)" % (
                                   address, manuf_id, 0x5449))
        dev_id = self._device.readU16BE(HDC1000_DEVICEID)
        if dev_id != 0x1000:
            raise RuntimeError("Device at '%x' has an unexpected "
                               "device id '%x' (Expected %x)" % (
                                   address, dev_id, 0x1000))

    ####################################################################
    #
    def reset(self):
        """
        reset, and select 14 bit temp & humidity
        """
        self._device.write16(HDC1000_CONFIG,
                             I2C.reverseByteOrder(HDC1000_CONFIG_RST |
                                                  HDC1000_CONFIG_MODE |
                                                  HDC1000_CONFIG_TRES_14 |
                                                  HDC1000_CONFIG_HRES_14))
        time.sleep(0.015)

    ####################################################################
    #
    def data(self):
        """
        Read the temperature and humidity and return them in a tuple
        (temperature, humidity)
        """
        temp_humid = self._read32(HDC1000_TEMP)

        # We read the two registers for temperature and humidity. Each
        # is 2 bytes. Each 16 bit word is in MSB order. Math is right
        # off of the data sheet.
        #
        temp = ((((temp_humid[0] << 8) + temp_humid[1]) / 65536.0) * 165) - 40
        humid = (((temp_humid[2] << 8) + temp_humid[3]) / 65536.0) * 100
        return (temp, humid)

    ####################################################################
    #
    def dry_sensor(self):
        """
        Cribbed from the Adafruit Arduino code. Guess it makes sure the
        sensor is ready for reading after normalizing in a room.
        """
        orig_config = self._device.readU16BE(HDC1000_CONFIG)

        # reset, heat up, and select 14 bit temp & humidity
        #
        new_config = I2C.reverseByteOrder(HDC1000_CONFIG_RST |
                                          HDC1000_CONFIG_HEAT |
                                          HDC1000_CONFIG_MODE |
                                          HDC1000_CONFIG_TRES_14 |
                                          HDC1000_CONFIG_HRES_14)
        self._device.write16(HDC1000_CONFIG, new_config)

        time.sleep(0.015)

        # Take 1000 readings and toss the results.
        #
        for i in range(1000):
            self._read32(HDC1000_TEMP)
            time.sleep(0.001)

        # Write our original config back out to the device.
        #
        self._device.write16(HDC1000_CONFIG, orig_config)
        time.sleep(0.015)

    ####################################################################
    #
    def _read32(self, register):
        """
        Read 4 bytes from the given register. Returned as a list of bytes.

        This does the waiting for the data to be read to be ready,
        catching IOError's while waiting.

        Keyword Arguments:
        register -- register to read from
        """
        # Write to the register that we want to start reading from
        #
        self._device.writeRaw8(register)

        # It takes some time for the device to actually do a reading so we wait
        # 10 milliseconds before trying to read.
        #
        time.sleep(0.01)

        # We then try a couple of times to read. We should get it on
        # the first read. However we will get an IOError (what smbus
        # sends when the device we are talking to sends a NAK) if it
        # is not ready to ready yet.
        #
        result = []

        for i in range(2):
            try:
                # We are going to read 4 bytes from the device.
                #
                for k in range(4):
                    result.append(self._device.readRaw8())

                # We get here if we managed to read 4 bytes.
                #
                break
            except IOError:
                # We got a NAK from the device. This is okay. Sleep a
                # bit and try again.
                #
                time.sleep(0.01)

        # If result's length is NOT 4 then we were not able to do
        # a full read and we will raise an IOError.
        #
        if len(result) != 4:
            raise IOError("Unable to read from HDC1000")

        return result
