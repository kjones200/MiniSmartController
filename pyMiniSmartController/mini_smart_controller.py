# !/usr/bin/env python

"""
Mini Smart Controller
------------------------------------------------------------
Retropie script for interactions between raspberry pi and smart controller.
"""

__author__ = 'Kenneth A Jones II'
__email__ = 'kenneth@nvnctechnology.com'

import serial
import time
import sys
import logging
from mscexception import MSCException

logger = logging.getLogger()

BELL = chr(7)
LF = chr(10)
CR = chr(13)

# Serial port baud rate
BAUD_RATE = 19200
TIMEOUT = None

# Serial commands
MSC_CMDS = {
    'init'            : 'I',
    'reset'           : 'R',
    'shutdown'        : 'S',
    'temperature'     : 'T',
    'firmware_version': 'v',
    'hardware_version': 'V',
    
}

# Reset codes
RESET_CODES = {
    'software': 1,
    'system'  : 2
}

# Default serial port
DEFAULT_PORT = "/dev/ttyS0"

# Acknowledgment
ACK = "OK"


class MiniSmartController(object):
    """
        Mini Smart Controller Class
    """
    
    def __init__(self):
        """
        Enable the raspberry p's miniUART which is /dev/ttyS0.

        :return:
        """
        self.serial_port = None
        self._temperature = 0
        self.fw_version = ""
        self.hw_version = ""
    
    def transmit(self, cmd):
        """ Transmit command to mini smart controller
        
        :param cmd: command string
        :return: response
        """
        logger.debug('tx: ' + cmd)
        self.serial_port.write(cmd + CR)
        return self.read_response()
    
    def read_response(self, timeout=.5):
        """
        Reads response from from the mini smart controller.

        :param timeout: Timeout period for a response.
        :return: The response
        """
        
        response = ""
        while True:
            try:
                b = self.serial_port.read(1)[0]
                if b == CR:
                    logger.debug('rx: ' + response)
                    return response
                elif b == BELL:
                    logger.debug("rx: %s" % BELL)
                    return response
                else:
                    response += b
            
            except:  # catch *all* exceptions
                logger.critical("unexpected error:", sys.exc_info()[0])
                return response
    
    def connect(self, port=DEFAULT_PORT):
        """
        Opens the serial port, clears pending characters and send close command
        to make sure that we are in configuration mode.
        
        :param port: Name of serial port
        :return:
        """
        try:
            self.serial_port = serial.Serial(port, BAUD_RATE, timeout=TIMEOUT)
            self.serial_port.flush()
            self.serial_port.flushInput()
            
            # Get mini smart controller information
            self.fw_version = self.transmit(MSC_CMDS['firmware_version'])[1:]
            self.hw_version = self.transmit(MSC_CMDS['hardware_version'])[1:]
        
        except serial.SerialException as e:
            raise MSCException("{0} - {1}: {2}".format(port, e.errno, e.strerror))
    
    def ack(self):
        """ Sends acknowledgement to the mini smart controller
        
        :return:
        """
        self.transmit(ACK)
    
    def init_msc(self):
        """
        Send the init command to mini smart controller.
    
        :return:
        """
        
        # Critical section, init command must be ACKed before continuing.
        while True:
            
            if self.transmit(MSC_CMDS['init']) == "OK":
                break  # ACK received
            else:
                time.sleep(1)  # Wait, then try sending the init command again
    
    def write_cpu_temperature(self, temperature):
        """
        Sends the CPU temperature to the RPI smart controllers
    
        :param temperature:
        :return:
        """
        self.transmit(MSC_CMDS['temperature'] + str(temperature))
