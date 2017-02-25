# !/usr/bin/env python

"""
Mini Smart Controller
------------------------------------------------------------
Retropie script for interactions between raspberry pi and smart controller.


THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, TITLE AND
NON-INFRINGEMENT. IN NO EVENT SHALL THE COPYRIGHT HOLDERS OR
ANYONE DISTRIBUTING THE SOFTWARE BE LIABLE FOR ANY DAMAGES OR
OTHER LIABILITY, WHETHER IN CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.
"""


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
    'cartridge'       : {'id'         : 'C',
                         'subcommands': ['r', 'w', 'e', 's']
                         },
    'init'            : {'id'         : 'I',
                         'subcommands': []
                         },
    'nofity'          : {'id'         : 'L',
                         'subcommands': ['0', '1']
                         },
    'reset'           : {'id'         : 'R',
                         'subcommands': ['0', '1']
                         },
    'power'           : {'id'         : 'P',
                         'subcommands': ['0', '1']
                         },
    'shutdown'        : {'id'         : 'S',  # this command is deprecated, but leaving for compatibility.  use 'power'
                         'subcommands': ['0', '1']
                         },
    'temperature'     : {'id'         : 'T',
                         'subcommands': []
                         },
    'firmware_version': {'id'         : 'v',
                         'subcommands': []
                         },
    'hardware_version': {'id'         : 'V',
                         'subcommands': []
                         }
}

# Default serial port
DEFAULT_PORT = "/dev/ttyS0"

# Acknowledgment
ACK = "OK"

# NFC
MAX_CONSOLE_LEN = 16
MAX_GAME_LEN = 96


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
    
    def transmit_get_response(self, cmd):
        """ Transmit command to mini smart controller and wait for response
        
        :param cmd: command string
        :return: response
        """
        logger.debug('tx: ' + cmd)
        self.serial_port.flush()
        self.serial_port.flushInput()
        self.serial_port.write(cmd + CR)
        time.sleep(.1)
        return self.read_response()
    
    def transmit(self, cmd):
        """ Transmit command to mini smart controller

        :param cmd: command string
        :return: response
        """
        logger.debug('tx: ' + cmd)
        self.serial_port.flush()
        self.serial_port.flushInput()
        self.serial_port.write(cmd + CR)
        time.sleep(.1)
    
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
                    logger.debug('rx: %s' % response)
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
            self.flush()
            
            # Get mini smart controller information
            self.fw_version = self.transmit_get_response(MSC_CMDS['firmware_version']['id'])[1:]
            self.hw_version = self.transmit_get_response(MSC_CMDS['hardware_version']['id'])[1:]
        
        except serial.SerialException as e:
            raise MSCException("{0} - {1}: {2}".format(port, e.errno, e.strerror))
    
    def flush(self):
        """ Flushes the serial port
        
        :return:
        """
        self.serial_port.flush()
        self.serial_port.flushInput()
    
    def ack(self):
        """ Sends acknowledgement to the mini smart controller
        
        :return:
        """
        self.transmit(ACK)  # don't expect response
    
    def get_all_commands(self):
        """ Get all mini smart controller commands
        
        :return: list of commands
        """
        result = []
        for key, value in MSC_CMDS.iteritems():
            result.append(value['id'])
        
        return result
    
    def get_subcommands(self, cmdid):
        """ Get subcommands for specified commands

        :param cmdid: command id
        :return: list of sub commands for command
        """
        result = []
        for key, value in MSC_CMDS.iteritems():
            if value['id'] == cmdid:
                return value['subcommands']
        
        return result
    
    def init_msc(self):
        """
        Send the init command to mini smart controller.
    
        :return:
        """
        
        # Critical section, init command must be ACKed before continuing.
        while True:
            
            if self.transmit_get_response(MSC_CMDS['init']['id']) == ACK:
                break  # ACK received
            else:
                time.sleep(1)  # Wait, then try sending the init command again
    
    def write_cpu_temperature(self, temperature):
        """
        Sends the CPU temperature to the RPI smart controllers
    
        :param temperature:
        :return:
        """
        self.transmit_get_response(MSC_CMDS['temperature']['id'] + str(temperature))
    
    def read_cart(self):
        """ Reads the emulator name and game name from a NFC cartridge

        :return: response
        """
        
        result = self.transmit_get_response(MSC_CMDS['cartridge']['id'] + MSC_CMDS['cartridge']['subcommands'][0])
        
        if result != 2:
            r = result[2:].rstrip().split(',')
            return [r[0].rstrip(), r[1].rstrip()]
        else:
            return ["", ""]
    
    def write_cart(self, emulator, game):
        """ Writes the emulator name and game name to a NFC cartridge

        :param emulator: emulator name
        :param game: game name
        :return: response
        """
        payload = ','.join([emulator.ljust(MAX_CONSOLE_LEN), game.ljust(MAX_GAME_LEN)])
        result = self.transmit_get_response(MSC_CMDS['cartridge']['id'] +
                                            MSC_CMDS['cartridge']['subcommands'][1] +
                                            payload)
        return int(result[2:])
    
    def erase_cart(self):
        """ Erase emulator and game information from NFC cartridge

        :return: response
        """
        result = self.transmit_get_response(MSC_CMDS['cartridge']['id'] + MSC_CMDS['cartridge']['subcommands'][2])
        return int(result[2:])
    
    def get_cart_status(self):
        """ Get the cartridge status
        
        :return: The cart status
        """
        result = self.transmit_get_response(MSC_CMDS['cartridge']['id'] + MSC_CMDS['cartridge']['subcommands'][3])
        return int(result[2:])
    
    def notifyLED(self, success):
        """ Tells mini smart controller to indicate a success or fail
        :param success: variable indicating success or failure
        :return:
        """
        command = MSC_CMDS['nofity']['id']
        if success:
            command += MSC_CMDS['nofity']['subcommands'][1]
        else:
            command += MSC_CMDS['nofity']['subcommands'][0]
        self.transmit_get_response(command)
