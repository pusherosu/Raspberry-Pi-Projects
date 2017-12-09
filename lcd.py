#!/usr/bin/python

import RPi.GPIO as GPIO
import smbus
import time

from PCF8574 import PCF8574_GPIO
from Adafruit_LCD1602 import Adafruit_CharLCD
from TwitterAPI import TwitterAPI, TwitterOAuth

def cleanup():
	mcp.output(3,0)
	lcd.clear()
	bus.close()

def scroll(lcd, text, pause1=False, pause2=False, rep=False):
	#timing defaults
	PAUSE_NEXT = 2
	PAUSE_REP = 2
	REPETITIONS = 1

	if pause1: PAUSE_NEXT = pause1
	if pause2: PAUSE_REP = pause2
	if rep: REPETITIONS = rep

	n=16
	rows = [text[i:i+n] for i in range (0, len(text), n)]
	n_rows = len(rows)
	for i in range (REPETITIONS):
		for x in range (n_rows):
			lcd.home()
			lcd.clear()
			nxt = x + 1
			lcd.message(rows[x]+"\n")
			if nxt == n_rows:
				time.sleep(2)
				break
			else:
				lcd.message(rows[nxt])
				time.sleep(PAUSE_REP)
	lcd.clear()

##########SETUP##########

o=TwitterOAuth.read_file()
try:
	api = TwitterAPI(       o.consumer_key,
        	                o.consumer_secret,
                	        o.access_token_key,
                        	o.access_token_secret)
except Exception as e:
	print ('TAPI Error:', e)

SEARCH_TERM = '#christmas'
lcd_addr = 0x3f
bus=smbus.SMBus(1)

try:
	mcp = PCF8574_GPIO(lcd_addr)
except Exception as e:
	print ('I/O Error: ',e)

try:
	lcd = Adafruit_CharLCD(pin_rs=0, pin_e=2, pins_db=[4,5,6,7], GPIO=mcp)
except Exception as e:
	print ('Init error: ',e)

mcp.output(3,1)
lcd.begin(16,2)

if __name__ == '__main__':

	msg_count = 0
	r = api.request('search/tweets',{'q': SEARCH_TERM})
	for item in r:
		MSG = item['text'] if 'text' in item else item
		scroll(lcd, MSG)
		msg_count += 1
	cleanup()
