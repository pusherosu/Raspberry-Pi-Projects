#!/usr/bin/python3

import smbus
import sys
import RPi.GPIO as GPIO
from threading import Timer, Thread, Event
from datetime import datetime
from time import sleep
from TwitterAPI import TwitterAPI, TwitterOAuth
from PCF8574 import PCF8574_GPIO
from Adafruit_LCD1602 import Adafruit_CharLCD

if sys.version_info[0] < 3:
	raise ValueError ("This script requires Python 3")
	
o=TwitterOAuth.read_file()
try:
	api = TwitterAPI(       o.consumer_key,
        	                o.consumer_secret,
                	        o.access_token_key,
                        	o.access_token_secret)
except Exception as e:
	print ('TAPI Error:', e)

SEARCH_TERM = '#christmas'
MAX_BUFFER = 10
tweet_queue = []
lcd_addr = 0x3f
bus=smbus.SMBus(1)

class perpetualTimer():

	def __init__(self, t, hFunction):
		self.t = t
		self.hFunction = hFunction
		self.thread = Timer(self.t, self.handle_function)

	def handle_function(self):
		self.hFunction()
		self.thread = Timer(self.t, self.handle_function)
		self.thread.start()

	def start(self):
		self.thread.start()

	def cancel(self):
		self.thread.cancel()
		
def print_from_buffer():
	if len(tweet_queue) == 0:
		pass
	else:
		scroll(lcd, tweet_queue[0])
		tweet_queue.pop(0)
	sleep(1)
	
def scroll(lcd, text, pause1=False, pause2=False, rep=False):
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
				sleep(2)
				break
			else:
				lcd.message(rows[nxt])
				sleep(PAUSE_REP)
	lcd.clear()
	
def monitor_stream():
	print("Starting...")
	r = api.request('statuses/filter', {'track': SEARCH_TERM})
	for item in r:
		if len(tweet_queue) >= MAX_BUFFER:
			tweet_queue.clear()
		elif len(tweet_queue) < MAX_BUFFER:
			tweet_queue.append(item['text']) if 'text' in item else item
		
def cleanup():
	mcp.output(3,0)
	lcd.clear()
	bus.close()
	
if __name__ == "__main__":
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

	t = perpetualTimer(1, print_from_buffer)
	t.start()
	monitor_stream()
