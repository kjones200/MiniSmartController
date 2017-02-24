# Mini Smart Controller

Mini Smart Controller is a simple electronics kits used in mini NES builds and more.

<img src="http://i.imgur.com/hKMNzRW.png" width="500">

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


## Front Panel Button Operations

#### KIT 1A
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
| power        | momentary  | turn on system. if valid cartridge, launch game   | if valid cartridge launch game; otherwise nothing        | eject game        |   
| power        | 3 seconds  | nothing        | shutdown        | shutdown        |
| reset        | momentary  | nothing        | nothing        | reset game        | 
| reset        | 3 seconds  | nothing        | if cartridge detected, write last played game; otherwise nothing        | if cartridge detected, write last played game; otherwise nothing        |


#### KIT 1B
Button operation for KIT1B non NFC systems:

|  button 	   | duration   | off        | in es      | in game    |
| ------------ | ----------	| ---------- | ---------- | ---------- |
| power        | latching   | turn on    | turn off   | turn off   |
| power        |    ---     |    ---     |    ---     |    ---     |
| reset        | momentary  | nothing    | nothing    | reset game | 
| reset        | 3 seconds  | nothing    | reset      | reset      |


## Kit Installation

1. Install USB extender harness and route cable under the raspberry pi. Hot glue and CA glue may used to hold down cables.
 
    <img src="http://i.imgur.com/IfsR2J1.png" width="500">

2. Glue switch mount to the base of the shell.
  
    <img src="http://i.imgur.com/eJFbQAH.jpg" width="500">
    
3. Install the raspberry pi with the USB extender.
    
    <img src="http://i.imgur.com/2QyfwHJ.png" width="500">

4. Optional: Connect fan to 4 pin fan connector.

    <img src="http://i.imgur.com/J800hVu.png" width="250"> <img src="http://i.imgur.com/icBM4Rt.png" width="250">
    
5. Connect front panel cable to the main PCB.
    
    <img src="http://i.imgur.com/PbAjzsu.png" width="500">

6. Install main PCB.
    
    <img src="http://i.imgur.com/aSuW1Sm.png" width="500">
   

## Front Panel LED Operation
| PATTEN              	| STATUS                                                                             	|
|---------------------	|------------------------------------------------------------------------------------	|
| Flash every 3 seconds 	| Mini smart controller is idle.                                                     	|
| Flashing (rapid)    	| Raspberry Pi has been powered on (or reset); waiting for boot sequence to complete 	|
| Flash every second   	| Raspberry Pi is shutting down                                                      	|
| Permanent on        	| Raspberry Pi boot sequence has completed                                           	|


## Firmware Update

This section only needs to be preformed if the mini smart controller firmware needs to be updated or changed.  

**NOTE:** All mini smart controllers ship with the latest firmware pre-loaded.

1. Disconnect power source from mini smart controller.
2. Short circuit (short) the bootloader jumper (P6) and connect mini smart controller to a USB host. The red LED (D1) will flash repeatedly once recognized by the USB host.  Reference pictures below:

    <img src="http://i.imgur.com/XFgoiSC.png" width="100"/> 
    <img src="http://i.imgur.com/jMDuq5c.png" width="100"/>
    
3. Open the application called HIDBootloader([download from here](https://github.com/kjones200/minismartcontroller/tree/master/dist/HIDBootloader/bin)) to update the firmware.
4. Click on File > Import Firmware Image and select the desire firmware image.

    <img src="http://i.imgur.com/w9QFH9G.png" width="500"/>
 
5. Click on Program > Erase/Program/Verify Device to upload the firmware image onto the mini smart controller.

    <img src="http://i.imgur.com/lVIWfq8.png" width="500"/>
    
6. Once the image has been successfully loaded, unplug mini smart controller from host and remove bootloader jumper (P6).

    <img src="http://i.imgur.com/UpB76Du.png" width="100"/>
    <img src="http://i.imgur.com/mqQxmSG.png" width="100"/>
     
6. Update complete.

## Retropie Installation and Configuration
1. Follow sections 1-3 from the [Retropie First Installation Guide](https://github.com/RetroPie/RetroPie-Setup/wiki/First-Installation#hardware-needed).

2. Open the *RetrioPie* Menu by pressing the 'A' key with the retropie icon highlighted.
    
    <img src="https://s25.postimg.org/c7x8loq6n/retroarch.png" width="500">
3. Go into *RETROARCH* > *Settings* > *Configuration* and enable *Save Configuration On Exit*
    
    <img src="https://s25.postimg.org/gv3angdjj/retroarch1.png" width="500">
4. Go down to 'Network' and enable 'Network Commands' and change *Network Command* Port to 55355.
    
    <img src="https://s25.postimg.org/93mkow9e7/retroarch2.png" width="500">
5. Exit this menu to save the settings
6. SSH into retropie.
7. Install the Python dependencies. NOTE: Some dependencies are not needed, yet, so lets just get them now.
    
    ```
    sudo apt-get update
    
    sudo apt-get install python-dev python-pip python-gpiozero
    
    sudo pip install psutil pyserial
    ```
8. Press 'y' if prompted to download and install.
9. Change the default settings for the serial port

    ```
    sudo raspi-config
    ```
    <img src="https://s25.postimg.org/9a09rzij3/Screen_Shot_2017_02_04_at_6_03_19_PM.png" width="500">
10. Scroll down to 'Advanced Options' then 'Serial' and select 'No', then 'Finish' to exit.
    
    <img src="https://s25.postimg.org/82mbzrsen/Screen_Shot_2017_02_04_at_6_40_33_PM.png" width="250"> <img src="https://s25.postimg.org/4cmp6vgjz/Screen_Shot_2017_02_04_at_6_03_33_PM.png" width="250">

11. Edit the boot config to enable the serial port for use in the script.
    ```
    sudo nano /boot/config.txt
    ```

12. Scroll down using your arrow keys and change 'enable_uart=0' to 'enable_uart=1.
    
    <img src="https://s25.postimg.org/65plv71qn/Screen_Shot_2017_02_04_at_6_04_24_PM.png" width="500">
13. Hit 'Ctrl+X' then 'y' and finally 'Enter' to save and exit.

## Script Installation
1. Download the mini smart controller repository

    ```
    cd ~/
    git clone https://github.com/kjones200/minismartcontroller.git
    ```
2. Copy retropie script files *runcommand-onend.sh,runcommand-onestar.sh, and autostart.sh* to */opt/retropie/config/all* by enter following command:
    ```
    cp *.sh /opt/retropie/config/all
    
    or
    
    sudo cp *.sh /opt/retropie/config/all

    ```
    NOTE: If Permission denied error is received, re-enter the command with *sudo* pre-appended. 
    
4. Hit 'Ctrl+X' then 'y' and finally 'Enter' to save and exit.

5. Script installation is now complete, now [reboot](https://www.youtube.com/watch?v=fuEJWmxWkKw)

    ```
    sudo reboot now
    ```

## Upgrading Kit 1A/1B to Kit 1A/1B NFC
This section should only be completed by users upgrading their current mini smart controller kit with a NFC reader.  For
new installations, please start [here](https://github.com/kjones200/minismartcontroller#retropie-installation-and-configuration)

1. SSH into retropie.
2. Download the latest version of the mini smart controller script

    ```
    cd ~/minismartcontroller
    git reset --hard HEAD
    git pull
    ```
3. Modify the *rc.local* file

    ```
    sudo nano /etc/rc.local
    ```
4. Remove the command *python /home/pi/minismartcontroller/pyMiniSmartController/py_msc.py &* by either deleting the command or commenting out the command.  In the example below, the command is commented out by place the '#' and the beginning of the line. 
    
    <img src="http://i.imgur.com/O6Uas3J.png" width="500">

5. Hit 'Ctrl+X' then 'y' and finally 'Enter' to save and exit.

6. Copy retropie script files *runcommand-onend.sh,runcommand-onestar.sh, and autostart.sh* to */opt/retropie/config/all* by enter following command:
    ```
    cp *.sh /opt/retropie/config/all
    
    or
    
    sudo cp *.sh /opt/retropie/config/all

    ```
    NOTE: If Permission denied error is received, re-enter the command with *sudo* pre-appended. 

7. Upgrade is now complete, now reboot.
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
2. Solder the new switch (MHP2273).  Use the switch mount as spacer to elevate the switch before soldering.
3. [Update firmware](https://github.com/kjones200/minismartcontroller/tree/master/dist/HIDBootloader/bin) with 'minismartcontroller_vX.X_kit1b.hex'

