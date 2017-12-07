#!/usr/bin/python

import time
import RPi.GPIO as GPIO
from TwitterAPI import TwitterAPI, TwitterOAuth

SEARCH_TERM = '#christmas'
LED_PIN = 7

#By default, credential information is saved in /home/username/.local/lib/pytho$
o=TwitterOAuth.read_file()
api = TwitterAPI(	o.consumer_key,
					o.consumer_secret,
					o.access_token_key,
					o.access_token_secret)

#Set up the GPIO pins
GPIO.setmode(GPIO.BOARD)
GPIO.setup(LED_PIN, GPIO.OUT)
GPIO.output(LED_PIN, GPIO.LOW)

def blink_led(duration):
	GPIO.output(LED_PIN, GPIO.HIGH)
	time.sleep(duration)
	GPIO.output(LED_PIN, GPIO.LOW)

#Twitter API request
r = api.request('statuses/filter' , {'track': SEARCH_TERM})

for item in r:
	blink_led(0.1)
	print(item['text'] if 'text' in item else item)
