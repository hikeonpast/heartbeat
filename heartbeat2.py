#!/usr/bin/env python3
import time
import signal
import sys
import logging

#used for Hue light control
import requests
import json

#static vars for Hue control; URL includes username and ID of target light
hue_hub_url = "http://192.168.1.84/api/XYNHOn3SOzXzZbhLpKBV2xlA5d9G9CeMcKQbt9oh/lights/29/state"

#logging.basicConfig(level=logging.DEBUG)

def signal_handler(sig, frame):
	print('Graceful Exit')

	#turn off hue light
	shutdown()

	sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

def shutdown():

        #turn off Hue on exit
	try:
        	r = requests.put(hue_hub_url, json.dumps({"on":False}), timeout=10)
	except:
                print ("HTTP error; can't turn off light")

#write update to Hue 
def update_hue(hue_color, hue_brightness, transition_centiseconds):

	#static vars
	hue_color_min = 0
	hue_color_max = 65535
	brightness_min = 0
	brightness_max = 255
	transition_min = 0
	transition_max = 10000

	if hue_color < hue_color_min:
		hue_color = hue_color_min
	elif hue_color > hue_color_max:
		hue_color = hue_color_max

	if hue_brightness < brightness_min:
		hue_brightness = brightness_min 
	elif hue_brightness > brightness_max:
                hue_brightness = brightness_max

	if transition_centiseconds < transition_min:
		transition_centiseconds = transition_min
	elif transition_centiseconds > transition_max:
		transition_centiseconds = transition_max

	#write update
	hue_payload = {"on":True, "sat":255, "hue": int(hue_color), "bri": int(hue_brightness), "transitiontime": int(transition_centiseconds)}
	
	try:
		r = requests.put(hue_hub_url, json.dumps(hue_payload), timeout=1)
	except: 
		print ("HTTP error; retrying")

while True:
	#defaults
	brightness = 0
	color = 58000
	transition_time = 0

	#time for full loop in ms
	loop_time = 1400

	# x intercepts for sawtooth heartbeat
	x0 = 0
	x1 = 300
	x2 = 500
	x3 = 700
	x4 = loop_time

	# y intercepts for sawtooth heartbeat
	peak_brightness = 180
	interim_brightness = 50
	end_brightness = 20

	for x in range(0,loop_time):
		if x == x0:
			brightness = peak_brightness
			transition_time = (x1-x0)/100
			#print("x: {} brightness: {} transition: {}".format(x, brightness, transition_time))
			update_hue(53000, brightness, transition_time)
		elif x == x1:
			brightness = interim_brightness
			transition_time = (x2-x1)/100
			#print("x: {} brightness: {} transition: {}".format(x, brightness, transition_time))
			update_hue(0, brightness, transition_time)
		elif x == x2:
			brightness = peak_brightness
			transition_time = (x3-x2)/100
			#print("x: {} brightness: {} transition: {}".format(x, brightness, transition_time))
			update_hue(53000, brightness, transition_time)
		elif x == x3:
			brightness = end_brightness
			transition_time = (x4-x3)/100
			#print("x: {} brightness: {} transition: {}".format(x, brightness, transition_time))
			update_hue(0, brightness, transition_time)

		if x % 10 == 0:
			time.sleep(0.01)

		


