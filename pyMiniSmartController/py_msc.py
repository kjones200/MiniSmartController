# !/usr/bin/env python

"""
Mini Smart Controller
------------------------------------------------------------
Main script to run on retropie.


THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, TITLE AND
NON-INFRINGEMENT. IN NO EVENT SHALL THE COPYRIGHT HOLDERS OR
ANYONE DISTRIBUTING THE SOFTWARE BE LIABLE FOR ANY DAMAGES OR
OTHER LIABILITY, WHETHER IN CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.
"""

__author__ = 'Kenneth A Jones II'
__email__ = 'kenneth@nvnctechnology.com'
__version__ = '1.1.0'

import time
import os
import sys
import socket
import logging
import argparse
import retropie
import psutil
import subprocess
import re

from mini_smart_controller import MiniSmartController
from mini_smart_controller import MSC_CMDS

logger = logging.getLogger()

# Script directory
SCRIPT_BASE = '/home/pi/minismartcontroller/pyMiniSmartController'
LOG_BASE = '/var/log'
ROM_DETAILS = 'romdetails.txt'

# Script sleep period
SLEEP_PERIOD = .1

# Mini smart controller object
msc = None

# Temperature sample period in seconds
temperature_ticks = 0
CPU_TEMPERATURE_SAMPLE_PERIOD = 60 / SLEEP_PERIOD

# Cartridge sample period in seconds
nfc_scan_ticks = 0
CARTRDIGE_SAMPLE_PERIOD = 5 / SLEEP_PERIOD

# addressing information of target
IPADDR = "127.0.0.1"
PORTNUM = 55355

# Cartridge
valid_cartridge = False
game_running = False
emulator_path = ""
rom_path = ""
current_console = "NONE"
current_game = "NONE"

def power_down():
    """ Initiate automated shutdown procedure for super-users to nicely notify users when the system is shutting
     down, saving them from system administrators, hackers, and gurus, who would otherwise not bother with such
     niceties.

    :return:
    """
    logger.debug('performing shutdown ...')
    subprocess.call('sudo shutdown -h now', shell=True)

def reboot():
    """ Initiate a system reboot
    
    :return:
    """
    logger.debug('performing OS reset ...')
    # subprocess.call('sudo reboot now', shell=True)

def retroarch(command):
    """ Sends commands to retroarch via socket
    
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
    subprocess.call('emulationstation &', shell=True)

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

def update_cpu_temperature():
    """ Handler for periodically for reading and sending the CPU temperature to the controller.

    :return:
    """
    global temperature_ticks

    if temperature_ticks > 0:
        temperature_ticks -= 1  # Still more time before sampling
        return

    temperature = int(float(acquire_cpu_temperature()))  # Get the CPU temperature and convert to integer
    msc.write_cpu_temperature(temperature)  # Send temperature to controller
    temperature_ticks = CPU_TEMPERATURE_SAMPLE_PERIOD  # Reset timer

def update_cartridge():
    """ Write console and rom to cartridge
    
    :return:
    """

    path = os.path.join(SCRIPT_BASE, ROM_DETAILS)
    subprocess.call('sudo chown pi -R ' + path, shell=True)

    try:
        with open(path) as f:
            results = f.readline().strip().split('/')[-2:]
            logger.debug('last played console=%s rom=%s' % (results[0], results[1]))
            success = msc.write_cart(results[0], results[1])
            logger.debug('cartridge update result=%d' % success)
            msc.notifyLED(success)
            time.sleep(1)
    except:
        logger.debug('failed to open "%s"' % path)
        msc.notifyLED(0)
        return

def task_scan_cartridge():
    """  Periodically scans for cartridge
    
    :return:
    """
    global nfc_scan_ticks

    if nfc_scan_ticks > 0:
        nfc_scan_ticks -= 1  # Still more time before sampling
        return

    scan_cartridge()
    nfc_scan_ticks = CARTRDIGE_SAMPLE_PERIOD

def scan_cartridge():
    """ Scans for a NFC cartridge
    
    :return:
    """

    global nfc_scan_ticks

    if nfc_scan_ticks > 0:
        nfc_scan_ticks -= 1  # Still more time before sampling
        return

    r = msc.read_cart()
    logger.debug('emulator: "%s"' % r[0])
    logger.debug('game    : "%s"' % r[1])
    validate_cartridge(r[0], r[1])

def validate_cartridge(console, game):
    """ Checks if the console and game are valid
    
    :param console: name of console
    :param game: name of game
    :return: 1 if valid; otherwise false
    """
    global valid_cartridge
    global emulator_path
    global rom_path

    if (is_valid_console(console) == True) and (is_valid_game(console, game) == True):
        emulator_path = get_emulator_path(console)
        rom_path = get_game_path(console, game)
        valid_cartridge = True
        logger.debug('cartridge is valid')
        return True

    emulator_path = ""
    rom_path = ""
    valid_cartridge = False
    logger.debug('invalid or no cartridge')
    return False

def is_valid_console(console):
    """ Checks if console is valid
    
    :param console: name of console
    :return: true if valid; otherwise false
    """
    global current_console

    console = console.strip().lower()  # remove leading and trailing whitespace and force to lower case

    if console in retropie.EMULATORS:
        current_console = console
        logger.debug('console "%s" is valid' % console)
        return True

    current_console = "NONE"
    logger.debug('could not find "%s" in supported consoles list' % console)
    return False

def is_valid_game(console, game):
    """ Checks if game(rom) is valid
    
    :param console: name of console
    :param game: name of game
    :return: True if valid; otherwise False
    """
    global current_game

    game_path = get_game_path(console, game)

    if os.path.isfile(game_path):
        current_game = game
        logger.debug('found "%s"' % game_path)
        return True

    current_game = "NONE"
    logger.debug('could not find "%s"' % game_path)
    return False

def get_emulator_path(console):
    """ Build the full path of the emulator
    
    :param console: name of console
    :return: full path of emulator
    """
    path = retropie.EMULATOR_BASE + console + " "
    logger.debug('emulator path "%s"' % path)
    return path

def get_game_path(console, game):
    """ Build the full path of the rom
    
    :param console: name of console
    :param game: name of game
    :return: full path of game
    """
    path = os.path.join(retropie.ROM_BASE, console, game)
    logger.debug('game path "%s"' % path)
    return path

def power_pressed():
    """ Starts or stop game when power button is momentarily pressed
    
    :return:
    """
    global game_running

    logger.debug('power button pressed')

    if game_running == False:
        scan_cartridge()  # scan for cartridge first
        game_running = start_game()

    else:
        eject_game()
        game_running = False

def start_game():
    """ Starts game detailed by game in cartridge
    
    :return: True when started; otherwise false
    """
    if valid_cartridge == True:
        logger.debug('loading "%s" with "%s" ...' % (current_console, current_game))
        kill_tasks(retropie.PROCESS_NAMES_EXTRA)
        #subprocess.call('sudo openvt -c 1 -s -f %s"%s" &' % (emulator_path, rom_path), shell=True)
        subprocess.call('%s"%s" &' % (emulator_path, rom_path), shell=True)
        subprocess.call("sudo chown pi -R /dev/shm", shell=True)  # ES needs permission as 'pi' to access this later
        
        return True

    logger.debug('no valid cartridge inserted or detected')
    return False

def eject_game():
    """ Exits currently running game
    
    :return:
    """
    logger.debug('ejecting "%s" running on "%s" ...' % (current_game, current_console))

    if process_exists("emulationstation"):
        logger.debug('emulationstation is running ...')
        time.sleep(1)

    else:
        kill_tasks(retropie.PROCESS_NAMES)
        start_es()

def parse_line(buf):
    """ Parses string of data for commands

    :param buf: string of data
    :return:
    """

    if buf[0] not in msc.get_all_commands():
        logger.debug('unknown command "%s" len: %d' % (buf[0], len(buf)))
        return

    if buf[0] == MSC_CMDS["reset"]['id']:
        subcommands = msc.get_subcommands(buf[0])

        if buf[1] in subcommands:
            msc.ack()

            if buf[1] == subcommands[0]:
                retroarch("RESET")

            elif buf[1] == subcommands[1]:
                update_cartridge()

        else:
            logger.debug('unknown reset code "%s"' % buf[1])

    elif buf[0] == MSC_CMDS["shutdown"]['id']:
        msc.ack()
        power_down()

    elif buf[0] == MSC_CMDS["power"]['id']:
        subcommands = msc.get_subcommands(buf[0])
        if buf[1] in subcommands:
            msc.ack()

            if buf[1] == subcommands[0]:
                power_pressed()

            elif buf[1] == subcommands[1]:
                power_down()

        else:
            logger.debug('unknown power code "%s"' % buf[1])

    elif buf[0] == MSC_CMDS["cartridge"]['id']:
        subcommands = msc.get_subcommands(buf[0])

        if buf[1] in subcommands:
            if buf[1] == subcommands[0]:
                emulator, game = msc.read_cart()
                logger.debug('emulator: "%s"' % emulator)
                logger.debug('game    : "%s"' % game)

            elif buf[1] == subcommands[1]:
                success = msc.write_cart(buf[2:].rstrip())
                logger.debug('write cartridge return code: "%s"' % success)

            elif buf[1] == subcommands[2]:
                success = msc.erase_cart()
                logger.debug('erase cartridge return code: "%s"' % success)

        else:
            logger.debug('unknown cartridge code "%s"' % buf[1])

def kill_tasks(procnames):
    """
    Kills all tasks specified
    :return:
    """
    logger.debug('killing task ...')
    for proc in psutil.process_iter():
        if proc.name() in procnames:
            pid = str(proc.as_dict(attrs=['pid'])['pid'])
            name = proc.as_dict(attrs=['name'])['name']
            logger.debug('stopping... %s (pid:%s)' % (name, pid))
            subprocess.call(["sudo", "kill", "-15", pid])

    # kodi needs SIGKILL -9 to close
    kodiproc = ["kodi", "kodi.bin"]
    for proc in psutil.process_iter():
        if proc.name() in kodiproc:
            pid = str(proc.as_dict(attrs=['pid'])['pid'])
            name = proc.as_dict(attrs=['name'])['name']
            logger.debug('stopping... %s (pid:%s)' % (name, pid))
            subprocess.call(["sudo", "kill", "-9", pid])

def process_exists(proc_name):
    """
    Search list of process and find a specifically named process
    :param proc_name:
    :return: True if found; otherwise false
    """
    ps = subprocess.Popen("ps ax -o pid= -o args= ", shell=True, stdout=subprocess.PIPE)
    ps_pid = ps.pid
    output = ps.stdout.read()
    ps.stdout.close()
    ps.wait()
    for line in output.split("\n"):
        res = re.findall("(\d+) (.*)", line)
        if res:
            pid = int(res[0][0])
            if proc_name in res[0][1] and pid != os.getpid() and pid != ps_pid:
                return True
    return False

def check_exit_controller():
    """
    Check if the game exited via controller.  If exited via controller, ES needs to be restarted.
    :return:
    """
    global game_running

    if game_running == True:
        if process_exists('retroarch') == False:
            logger.debug('detected game exit via controller ...')
            # Game was exited from controller
            game_running = False
            start_es()

def main(args, log_level):
    """ Main function

    :param args: Command line arguments
    :param log_level: log level
    :return:
    """
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('[%(asctime)s] [%(levelname)-8s] %(message)s')

    # create the logging file handler
    fh = logging.FileHandler(os.path.join(SCRIPT_BASE, 'msc.log'), mode='w')
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

    global msc
    msc = MiniSmartController()  # Create instance of mini smart controller class
    msc.connect()  # Connect to serial port
    logger.debug("connected to mini smart controller fw %s, hw %s " % (msc.fw_version, msc.hw_version))
    msc.init_msc()  # Begin initialization with mini smart controller

    # simulate power button pressed to auto launch if valid cartridge is inserted
    power_pressed()

    if game_running:
        logger.debug('game launched, emulation station will not be started')
    elif args.emu:
        start_es()  # Start emulation station
    else:
        logger.debug('emulation station will not be started')

    line = ""

    # Run this script F-O-R-E-V-E-R
    while True:
        try:
            # Serial port task
            if msc.serial_port.inWaiting() > 0:
                line += msc.serial_port.read(msc.serial_port.inWaiting())
                if '\r' in line:
                    # full command received
                    logger.debug('rx: [main] %s' % line)
                    parse_line(line.strip())
                    msc.flush()
                    line = ""

            update_cpu_temperature()  # check CPU temperature
            # task_scan_cartridge()  # check cartridge
            # check_exit_controller()

            # Sleep
            time.sleep(SLEEP_PERIOD)

        except KeyboardInterrupt:
            logger.debug('keyboard interrupted')
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
        "-e",
        "--emu",
        help="start emulation station",
        action="store_true")

    args = parser.parse_args()

    # Setup log
    if args.verbose:
        loglevel = logging.DEBUG
    else:
        loglevel = logging.INFO

    main(args, loglevel)
