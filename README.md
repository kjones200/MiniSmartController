# Mini Smart Controller

Mini Smart Controller is a simple electronics kits used in mini NES builds and more.

### Key Features:
- Power controller (Power and reset switches)
- Fan controller with active cooling (supports 2, 3, and 4 pin fans)
- Expandable platform for adding new features and daughter boards.
- Bootloader for easy firmware updates.
- Zero soldering required.

#### Features to Come:
- NFC/RFID support
- Turn ON/OFF raspberry pi via bluetooth controller i.e Wii U Controller

This electronics kit comes with all necessary electronics, assemblies, and harnesses, excluding the micro USB cable, Raspberry Pi, and fan.

Here is what what is exactly is included:

- Main PCBA
- Front panel PCBA including a 3mm red LED, power switch, and reset switch.
- USB extender PCBAs; includes double stack USB jack
- 5 pin cable harness for connecting front panel to the main PCBA.
- 6 pin cable harness for relocating USB jack to front of the case.
- Micro USB input jack for power input.

Visit [Mini NES Builders](https://www.facebook.com/groups/miniNESbuilders/) for inspiration and help.

## Change Log
| Date       	| Notes           	|
|------------	|-----------------	|
| 2017-01-26 	| Initial release 	|
|

## Front Panel Button Operations

Button operation for non NFC systems:

|  button 	   | duration   | off        | in es      | in game    |
| ------------ | ----------	| ---------- | ---------- | ---------- |
| power        | momentary  | turn on    | nothing    | nothing    |
| power        | 3 seconds  | nothing    | shutdown   | shutdown   |
| reset        | momentary  | nothing    | nothing    | reset game | 
| reset        | 3 seconds  | nothing    | reset      | reset      |

Button operation for NFC systems:

|  button 	   | duration   | off        | in es      | in game    |
| ------------ | ----------	| ---------- | ---------- | ---------- |
| power        | momentary  | tbd        | tbd        | tbd        |   
| power        | 3 seconds  | tbd        | tbd        | tbd        |
| reset        | momentary  | tbd        | tbd        | tbd        | 
| reset        | 3 seconds  | tbd        | tbd        | tbd        |



## Front Panel LED Operation
| PATTEN              	| STATUS                                                                             	|
|---------------------	|------------------------------------------------------------------------------------	|
| Flash every 3 seconds 	| Mini smart controller is idle.                                                     	|
| Flashing (rapid)    	| Raspberry Pi has been powered on (or reset); waiting for boot sequence to complete 	|
| Flash every second   	| Raspberry Pi is shutting down                                                      	|
| Permanent on        	| Raspberry Pi boot sequence has completed                                           	|


## Firmware Update
1. Disconnect power source from mini smart controller.
2. Short bootloader jumper (P6) and connect mini smart controller to a USB host. The red LED (D1) will flash once recognize by the USB host.
3. Use bootloader application [MPHidFlash](https://github.com/ApertureLabsLtd/mphidflash/tree/master/binaries) to update the firmware.
4. Once MPHidFlash has been installed, type the following command line command to upload the firmware:
    ```
    mphidflash -w minismartcontroller_vX.X_kit1a.hex
    ```
5. Unplug mini smart controller from host and remove bootloader jumper (P6).
6. Update complete.

## Retropie Installation and Configuration
1. Follow sections 1-3 from the [Retropie First Installation Guide](https://github.com/RetroPie/RetroPie-Setup/wiki/First-Installation#hardware-needed).

2. SSH into retropie.
3. Install the Python dependencies. NOTE: Some dependencies are not needed, yet, so lets just get them now.
    ```
    sudo apt-get update
    sudo apt-get install python-dev python-pip python-gpiozero
    sudo pip install psutil pyserial
    ```
4. Press 'y' if prompted to download and install.
5. Change the default settings for the serial port
    ```
    sudo raspi-config
    ```
6. Scroll down to 'Advanced Options' then 'Serial' and select 'No', then 'Finish' to exit.
7. Edit the boot config to enable the serial port for use in the script.  Scroll down using your arrow keys and change 'enable_uart=0' to 'enable_uart=1'
8. Hit 'Ctrl+X' then 'y' and finally 'Enter' to save and exit.

## Script Installation
1. Download the mini smart controller repository
    ```
    cd ~/
    git clone https://github.com/kjones200/minismartcontroller.git
    ```
2. Modify rc.local to launch script at boot up
    ```
    sudo nano /etc/rc.local
    ```
3. Enter the following command just before 'exit 0':
    ```
    python /home/pi/minismartcontroller/pyMiniSmartController/py_msc.py &
    ```
4. Hit 'Ctrl+X' then 'y' and finally 'Enter' to save and exit.
5. Script installation is now complete, now [reboot](https://www.youtube.com/watch?v=fuEJWmxWkKw)
    ```
    sudo reboot now
    ```

## Convert Kit 1A to Kit 1B

The mini smart controller kit 1A can be converted to kit 1B.  Kit 1B uses a latching switch for the power button.

- Requirements:
    - Basic electronic knowlege of switches
    - Soldering experience
- Tool
    - Soldering iron
    - Vacuum de-soldering iron (Recommended [Vaccum Desolding Iron](https://www.amazon.com/Science-Purchase-Desoldering-Iron/dp/B00CUKTH2A/ref=sr_1_9?ie=UTF8&qid=1485560615&sr=8-9&keywords=vacuum+desoldering+iron))
    - Solder
    - Flux
    - Fume extractor (Optional)
- Bill of Materials
    - Kit 1B firmware ([firmware](https://github.com/kjones200/minismartcontroller/tree/master/firmware))
    - Pushbutton Switch 7mm DPDT ON - OFF ([MHP2273](http://www.mouser.com/ProductDetail/Apem/MHPS2273/?qs=sGAEpiMZZMvxtGF7dlGNpiWIsZK%2fBfC0yZ1ZBCme%252brc%3d))


1. De-solder the power switch from the front panel PCBA.
2. Solder the new switch (MHP2273)
3. Update firmware with 'minismartcontroller_vX.X_kit1b'
