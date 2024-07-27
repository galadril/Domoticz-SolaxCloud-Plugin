
# Domoticz-SolaxCloud

SolaxCloud Plugin for Domoticz home automation
This plugin allows you to see all the relevant information from your SolaxCloud of your Solar Inverter

More info about SolaxCloud:
https://global.solaxcloud.com


## Installation

Python version 3.4 or higher required & Domoticz version 3.87xx or greater.

To install:
* Go in your Domoticz directory using a command line and open the plugins directory.
* Run: ```git clone https://github.com/galadril/Domoticz-SolaxCloud-Plugin.git```
* Restart Domoticz.

## Devices
![image](https://github.com/user-attachments/assets/19ddc61a-a7b6-4e25-a71e-10b47ea92146)

![image](https://github.com/user-attachments/assets/68311361-522f-4e82-ab99-3943a27b83b9)


## Configuration

* Open the Domoticz web interface.
* Go to Setup > Hardware.
* Add a new hardware with under the type SolaxCloud.
* Set the Scan interval (in seconds) for how often the plugin should scan for SolaxCloud devices.
* Save and close the dialog.


## Updating

To update:
* Go in your Domoticz directory using a command line and open the plugins directory then the Domoticz-SolaxCloud-Plugin directory.
* Run: ```git pull```
* Restart Domoticz.


## Usage

The plugin will automatically discover compatible SolaxCloud devices on your local network and create/update devices in Domoticz. 


## Debugging

You can enable debugging by setting the Debug parameter to a value between 1 and 6 in the Setup > Hardware dialog. More information about the debugging levels can be found in the Domoticz documentation.


## Change log

| Version | Information |
| ----- | ---------- |
| 0.0.1 | Initial version |


# Donation

If you like to say thanks, you could always buy me a cup of coffee (/beer)!   
(Thanks!)  
[![PayPal donate button](https://img.shields.io/badge/paypal-donate-yellow.svg)](https://www.paypal.me/markheinis)
