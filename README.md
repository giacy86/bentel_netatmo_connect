# Bentel Netatmo Connect
*Automation of Netatmo thermostat mode (away/schedule) based on a GPIO input of a Raspberry PI*
## Introduction
This project was born because the [Netatmo smart thermostat](https://www.netatmo.com/it-it/smart-thermostat) does not have any sort of geofencing functions in the mobile app and therefore you must remember to manually set the absent mode so as not to waste energy unnecessarily.
![Away mode](https://github.com/giacy86/bentel_netatmo_connect/blob/5dd52b1f3eff4c47f5ec212c15a1331fd104158d/resources/Screenshot%202023-12-28%20alle%2008.36.56%20-%20dimensioni%20medie.jpeg)
# How it works
The core is a python script inside a Raspberry PI that sets the away/schedule mode of the thermostat through the Netatmo API based on a GPIO input of the Raspberry PI.
I named this project *Bentel Netatmo connect* because i use an Open Collector output from the [Bentel Absoluta](https://www.bentelsecurity.com/index.php?n=products&o=view&id=388) home security system.
If GPIO is high the script set the thermostat mode to *schedule* or do nothing if the mode is *manual* (typically if you set a manual temperature before go home that is higher of the scheduled temperature); if GPIO is low the script set the thermostat mode to *away*.
A Telegram notification is also sent.

> [!NOTE]
> The OAuth2 tokens required by the Netatmo API, *access_token* and *refresh_token* are stored in a config file; other parameters are hard-coded into the script; customize them to your needs. (see [Setup section](https://github.com/giacy86/bentel_netatmo_connect/blob/main/README.md#setup))

# Schematic (for Bentel Absoluta)
![schematic](resources/bentel_netatmo_connect_v1_Schematic.svg)
# Prerequisites

 - RPi.GPIO python library - `pip install RPi.GPIO`
 - Requests python library `pip install requests`
 - Requests OAuth2 python library `pip install requests-oauth2`
 - Telegram BOT for notifications - see [here](https://core.telegram.org/bots/tutorial)
# Setup
 - Create an app in [Netatmo developer console](https://dev.netatmo.com/).
 - Set the variables `client_id` and `client_secret`
 - Set the variable `input` with the correct GPIO input used (see pinout [here](https://pinout.xyz/))
 - Set the variables `home_id` with your *home_id*: for retrieve it, go to [https://dev.netatmo.com/apidocumentation/energy#homesdata](https://dev.netatmo.com/apidocumentation/energy#homesdata), and execute *homesdata* API request ([https://api.netatmo.com/api/homesdata](https://api.netatmo.com/api/homesdata)) and get *home_id* in the response
 - Set the variables `telegram_chat_id` and `telegram_bot_token`
 - edit the full path of the settings file in `config.read('/home/user/netatmo.ini')`
 - go to [https://dev.netatmo.com/](https://dev.netatmo.com/), enter your app, scroll to *token generator*, choose the scopes *write_thermostat* and *read_thermostat* and click generate; accept the authorization page and then copy/paste the tokens in the config file [netatmo.ini](./netatmo.ini).
# Install as service Raspbian
Edit the file [bentel_netatmo_connect.service](./bentel_netatmo_connect.service) with your path in line `ExecStart=/usr/bin/python3 /home/user/bentel_netatmo_connect_v5.py` and place it to */etc/systemd/system* and enable the service with `sudo systemctl enable bentel_netatmo_connect.service`.
# Usage
`sudo service bentel_netatmo_connect start`