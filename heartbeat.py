#!/usr/bin/env python3
import time
import signal
import sys

#used for Hue light control
import requests
import json

#static vars for Hue control; URL includes username and ID of target light
hue_hub_url = "http://192.168.1.84/api/XYNHOn3SOzXzZbhLpKBV2xlA5d9G9CeMcKQbt9oh/lights/29/state"

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
def update_hue(hue_color, hue_brightness):

	#static vars
	hue_color_min = 0
	hue_color_max = 21845
	brightness_min = 0
	brightness_max = 255

	if hue_color < hue_color_min:
		hue_color = hue_color_min
	if hue_color > hue_color_max:
		hue_color = hue_color_max

	if hue_brightness < brightness_min:
		hue_brightness = brightness_min 
	if hue_brightness > brightness_max:
                hue_brightness = brightness_max

	#write update
	#hue_payload = {"on":True, "sat":255, "hue": hue_color, "bri": hue_brightness}
	hue_payload = {"bri": hue_brightness}
	
	try:
		r = requests.put(hue_hub_url, json.dumps(hue_payload), timeout=1)
	except: 
		print ("HTTP error; retrying")

while True:
	#defaults
	brightness = 0
	color = 0
	loops = 50

	#initialize bulb; try to limit verbosity on each update
	hue_payload = {"on":True, "sat":255, "hue": color, "bri": brightness}

	try:
		r = requests.put(hue_hub_url, json.dumps(hue_payload), timeout=1)
	except: 
		print ("HTTP error")	

	# x intercepts for sawtooth heartbeat
	x0 = 0
	x1 = 8
	x2 = 16
	x3 = 24
	x4 = loops

	# y intercepts for sawtooth heartbeat
	peak_brightness = 180
	interim_brightness = 60
	end_brightness = 20

	for x in range(0,loops):
		if x >= x0 and x < x1:
			brightness = end_brightness + ((x - x0) * ((peak_brightness-end_brightness)/(x1-x0)))
		elif x >= x1 and x < x2:
			brightness = peak_brightness - ((x - x1) * ((peak_brightness-interim_brightness)/(x2-x1)))
		elif x >= x2 and x < x3:
			brightness = interim_brightness + ((x - x2) * ((peak_brightness-interim_brightness)/(x3-x2)))
		elif x > x3:
			brightness = peak_brightness - ((x - x3) * ((peak_brightness-end_brightness)/(x4-x3)))

		brightness = int(brightness)
		#print("x: {} Brightness: {}".format(x, brightness))

		update_hue(color, brightness)
		time.sleep(0.025)

