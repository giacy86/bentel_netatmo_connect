import requests
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import TokenExpiredError
import configparser
from time import sleep
import RPi.GPIO as GPIO

# GPIO set up as input.
GPIO.setmode(GPIO.BCM)
input = 17
GPIO.setup(input, GPIO.IN)

current_state = 1

############ config file
config = configparser.ConfigParser()
config.read('/home/user/netatmo.ini')

####### netatmo parameters
client_id = r'xxxxxxxxxxxxxxxx'
client_secret = r'xxxxxxxxxxxxxxxx'
refresh_url = 'https://api.netatmo.com/oauth2/token'
home_id = r'xxxxxxxxxxxxxxxx'
############################

####### telegram parameters
telegram_chat_id = 'xxxxxxxxx'
telegram_bot_token = 'xxxxxxxxxx'
############################
extra = {
	'client_id' : client_id,
	'client_secret': client_secret
}

payload = {'home_id' : home_id}

token = {
	'access_token': config.get("DEFAULT", "access_token"),
	'refresh_token': config.get("DEFAULT", "refresh_token"),
	'token_type': 'Bearer',
	'expires_in': '10800',
}
###############################################
client = OAuth2Session(client_id, token=token)

	
# Save the new tokens in config file
def token_saver(token):
	config['DEFAULT']['refresh_token'] = token['refresh_token']
	config['DEFAULT']['access_token'] = token['access_token']
	with open('netatmo.ini', 'w') as configfile:
		config.write(configfile)


# get the current thermostat status and if token has expired refresh and saves the tokens	
def homestatus() :
	global token
	global client
	try:
	    r = client.get('https://api.netatmo.com/api/homestatus', params=payload)	
	    print(r.json()['body']['home']['rooms'][0]['therm_measured_temperature'])
	except TokenExpiredError as e:
		print('TOKEN EXPIRED!!!!!!')
		token = client.refresh_token(refresh_url, **extra)
		client = OAuth2Session(client_id, token=token)
		token_saver(token)
		r = client.get('https://api.netatmo.com/api/homestatus', params=payload)
		print(r.json()['body']['home']['rooms'][0]['therm_measured_temperature'])
		#sendTelegramNotification('bentel netatmo connect: token updated')
	return r
		

def sendTelegramNotification(str) :
        payload = {'chat_id' : telegram_chat_id,
                                'parse_mode' : "Markdown",
                                'text' : str
                                        }
        try:
                response = requests.get("https://api.telegram.org/bot"+str(telegram_bot_token)+"/sendMessage", params=payload)
                response.raise_for_status()
                return response
        except requests.exceptions.HTTPError as error:
                return error.response.status_code

# function setthermmode(Mode)
# set away/program mode (string), return the json if ok (status_code==200) else return the status code. If the thermostat is in manual mode return 0.
def setthermmode(Mode):
	payload = {'home_id' : home_id,
	           'mode' : Mode,
	          }
	try:
		therm_data_response = homestatus()           #get current thermostat data
		temperature = therm_data_response.json()['body']['home']['rooms'][0]['therm_measured_temperature']
		setpoint_mode = therm_data_response.json()['body']['home']['rooms'][0]['therm_setpoint_mode']
		setpoint_temp = therm_data_response.json()['body']['home']['rooms'][0]['therm_setpoint_temperature'] 
		
		#if Mode = away
		if Mode == 'away':
			response = client.get("https://api.netatmo.com/api/setthermmode", params=payload)
			response.raise_for_status()
			response_json = response.json()
			status = response_json['status']    #get response status
			str_schedule = "Impostazione del termostato in modalità assente: *"+str(status)+"*."
				
		#if Mode = schedule
		if Mode == 'schedule':
			if setpoint_mode == 'manual':   #if setpoint_mode is manual do nothing
				str_schedule = "Termostato già impostato in modalità manuale a *"+str(setpoint_temp)+"* °C."
				response_json = 0   #set the returned value
			else:   # else set Program mode
				response = client.get("https://api.netatmo.com/api/setthermmode", params=payload)
				response.raise_for_status()
				response_json = response.json()
				status = response_json['status']    #get response status
				str_schedule = "Impostazione del termostato in modalità programma: *"+str(status)+"*."

		str_schedule += " Temperatura attuale: *"+str(temperature)+"* °C."
		sendTelegramNotification(str_schedule)       #send Telegram notification
		return response_json
	except requests.exceptions.HTTPError as error:
			print(error.response.status_code, error.response.text)

	
try:
	while True:            # this will carry on until you hit CTRL+C
		if GPIO.input(input) != current_state: # if port 2 == 1
			print ("input changed")
			current_state = GPIO.input(input)   #change the current state
			if GPIO.input(input):   #if input is HIGH
				setthermmode("schedule")
			else:                   #if input is LOW
				setthermmode("away")   
			sleep(60)         # wait
		else:
			print ("input not changed")
			sleep(60)
finally:                   # this block will run no matter how the try block exits
   GPIO.cleanup()         # clean up after yourself