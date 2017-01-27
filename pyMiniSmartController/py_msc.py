# !/usr/bin/env python

"""
Mini Smart Controller
------------------------------------------------------------
Main script to run on retropie.
"""

__author__ = 'Kenneth A Jones II'
__email__ = 'kenneth@nvnctechnology.com'
__version__ = '1.0.0'

import time
import os
import sys
import socket
import logging
import argparse
from subprocess import call
from mini_smart_controller import MiniSmartController
from mini_smart_controller import MSC_CMDS
from mini_smart_controller import RESET_CODES

logger = logging.getLogger()

# Script sleep period
SLEEP_PERIOD = .1

# Temperature sample period in seconds
CPU_TEMPERATURE_SAMPLE_PERIOD = 60 / SLEEP_PERIOD

# addressing information of target
IPADDR = "127.0.0.1"
PORTNUM = 55355

# Timer ticks
temperature_ticks = 0

def shutdown(msc_obj):
    """ Initiate automated shutdown procedure for super-users to nicely notify users when the system is shutting
     down, saving them from system administrators, hackers, and gurus, who would otherwise not bother with such
     niceties.
    :param msc_obj: serial port object
    :return:
    """
    logger.debug('performing shutdown ...')
    call('sudo shutdown -h now', shell=True)
    sys.exit(0)

def reboot(msc_obj):
    """ Initiate a system reboot
    
    :param msc_obj: serial port object
    :return:
    """
    logger.debug('performing OS reset ...')
    call('sudo reboot now', shell=True)
    sys.exit(0)

def retroarch(msc_obj, command):
    """ Sends commands to retroarch via socket
    
    :param msc_obj: serial port object
    :param command: retroarch command
    :return:
    """

    logger.debug('performing "%s" command to %s:%d ...' % (command, IPADDR, PORTNUM))
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Open socket
    s.sendto(command, (IPADDR, PORTNUM))  # Send command to local host

def start_es():
    """ Starts emulation station
    
    :return:
    """
    logger.debug('launching emulation station ...')
    call('emulationstation &', shell=True)

def acquire_cpu_temperature():
    """
    Reads the CPU temperature using "vcgencm measure_temp"

    :return: CPU temperature
    """

    # Read CPU temperature
    logger.debug('reading CPU temperature ...')
    res = os.popen('vcgencmd measure_temp').readline()
    logger.debug(res.replace('\n', ''))
    return res.replace("temp=", "").replace("'C\n", "")

def update_cpu_temperature(msc_obj):
    """ Handler for periodically for reading and sending the CPU temperature to the controller.

    :param msc_obj: serial port object
    :return:
    """
    global temperature_ticks

    if temperature_ticks > 0:
        temperature_ticks -= 1  # Still more time before sampling
        return

    temperature = int(float(acquire_cpu_temperature()))  # Get the CPU temperature and convert to integer
    msc_obj.write_cpu_temperature(temperature)  # Send temperature to controller
    temperature_ticks = CPU_TEMPERATURE_SAMPLE_PERIOD  # Reset timer

def parse_line(msc_obj, buf):
    """ Parses string of data for commands

    :param msc_obj: serial port object
    :param buf: string of data
    :return:
    """
    if not buf[0] in MSC_CMDS.values():
        logger.debug('unknown command "%s"' % buf[0])
        return  # Unknown command

    if buf[0] == MSC_CMDS["reset"]:
        if int(buf[1]) == RESET_CODES["software"]:
            msc_obj.ack()
            retroarch(msc_obj, "RESET")
        elif int(buf[1]) == RESET_CODES["system"]:
            msc_obj.ack()
            reboot(msc_obj)
        else:
            logger.debug('unknown reset code "%s"' % buf[1])
    elif buf[0] == MSC_CMDS["shutdown"]:
        msc_obj.ack()
        shutdown(msc_obj)

def main(args, log_level):
    """ Main function

    :param args: Command line arguments
    :param log_level: log level
    :return:
    """
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('[%(asctime)s] [%(levelname)-8s] %(message)s')

    # create the logging file handler
    fh = logging.FileHandler("msc_log.txt")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)

    # create stdout handler
    ch = logging.StreamHandler()
    ch.setLevel(log_level)
    ch.setFormatter(formatter)

    # add handlers to logger object
    logger.addHandler(fh)
    logger.addHandler(ch)

    logger.debug('pyMiniSmartController v%s ...' % __version__)

    if args.emu:
        start_es()  # Start emulation station
    else:
        logger.debug('emulation station will not be started')

    msc = MiniSmartController()  # Create instance of mini smart controller class
    msc.connect()  # Connect to serial port
    logger.debug("connected to mini smart controller fw %s, hw %s " % (msc.fw_version, msc.hw_version))
    msc.init_msc()  # Begin initialization with mini smart controller

    line = ""

    # Run this script F-O-R-E-V-E-R
    while True:
        try:
            # Serial port task
            if msc.serial_port.inWaiting() > 0:
                line += msc.serial_port.read(msc.serial_port.inWaiting())
                if '\r' in line:
                    # full command received
                    logger.debug('rx: %s' % line)
                    parse_line(msc, line)

            # Check if it time to sample the
            update_cpu_temperature(msc)

            # Sleep
            time.sleep(SLEEP_PERIOD)

        except KeyboardInterrupt:
            logger.info('keyboard interrupted')
            sys.exit(0)

        except:  # catch *all* exceptions
            logger.critical("unexpected error:", sys.exc_info()[0])

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="This script decodes a mapped object value.  The ouput is the index from the OD, subindex from "
                    "the OD, and data length in bits.",
        epilog="",
        fromfile_prefix_chars='@')

    # Specify parameters
    parser.add_argument(
        "-v",
        "--verbose",
        help="increase output verbosity",
        action="store_true")

    parser.add_argument(
        "-d",
        "--debug",
        help="debug output verbosity",
        action="store_true")

    parser.add_argument(
        "-e",
        "--emu",
        help="start emulation station",
        action="store_true")

    args = parser.parse_args()

    # Setup log
    if args.verbose:
        loglevel = logging.CRITICAL
    elif args.debug:
        loglevel = logging.DEBUG
    else:
        loglevel = logging.INFO

    main(args, loglevel)
