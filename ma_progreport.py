#!/usr/bin/env python
import requests, time

from time import localtime, strftime

from luma.core.interface.serial import spi, noop
from luma.core.render import canvas
from luma.core.legacy import text, textsize
from luma.core.legacy.font import proportional, LCD_FONT
from luma.led_matrix.device import max7219

serial = spi(port=0, device=0, gpio=noop(), bus_speed_hz=500000)
device = max7219(serial, cascaded=4, block_orientation=-90, rotate=0)

from PIL import ImageFont

# font = ImageFont.truetype("/home/pi/luma.examples/examples/fonts/pixelmix.ttf", 8)

joburl = 'http://localhost/api/job?apikey=0B565C162E6D45D698825F4E1F210A25'
tecurl = 'http://localhost/api/printer/tool?apikey=0B565C162E6D45D698825F4E1F210A25'
cleaner = 0
last_compl = 999
last_heat = 999
tooltemp = 0
noClock = 0
noHeat = 0
clockDelay = 30 # amount of loops of unchanged data until clock display

while True:
	startX = 0
	cleaner = cleaner + 1
	myHeat = "---.-c"
	
	# periodic re-init of display
	
	if cleaner >= 10:
		# close and re-open, fixed issues with unstable display cable
		device.cleanup()
		serial = spi(port=0, device=0, gpio=noop(), bus_speed_hz=500000)
		device = max7219(serial, cascaded=4, block_orientation=-90, rotate=0)
		cleaner = 0
	
	# prepare default display

	myClock = strftime('%H:%M', localtime() )

	# try to read data from octoprint API
	
	try:
	
		myMode = 'regular'
		
		r = requests.get( joburl )
		compl = r.json()['progress']['completion']
		myCompl = '{:6.3f}'.format( compl )

		r = requests.get( tecurl )
		tooltemp = r.json()['tool0']['actual']
		myHeat = '{:05.1f}c'.format( tooltemp )
			
	except:
		myText = strftime('%H:%M', localtime() )
		startX = 3
		myMode = 'nodata'

	myContrast = 20
	
	if myMode == 'regular' :

		myText = myCompl # Priority for Progress
	
		if( last_compl != compl and last_compl != 100):
			noClock = clockDelay
			noHeat = 5 # a short delay to mask out long linear moves that do not increase progress

		if noHeat == 0:

			# show tooltemp if no progress for 3 loops
			myText = myHeat
									
			#  but also only if actively heating
									
			if tooltemp > 50:
				noClock = clockDelay

		else:
			noHeat = noHeat - 1 

	# fall back to clock on error or after noClock has run out

	if noClock > 0 :
		noClock = noClock - 1

	if noClock == 0 or myMode == 'nodata':
		myText = myClock
		startX = 3
		myContrast = 20
			
	# memorize for next loop
			
	last_compl = compl
	last_heat = myHeat

	# paint something now
		
	device.contrast( myContrast )

	for flashloop in [0,1]:

		curX = startX
		
		with canvas(device) as draw:
		# tWidth = textsize( compl, font = proportional( LCD_FONT ) )
		# tWidth = textsize( compl )
		# tX = int( ( 32 - tWidth[0] ) / 2 ) 
		# draw.rectangle(device.bounding_box, outline="white", fill="black")

			maxL = 6
			for myChar in myText:
				maxL = maxL - 1
				if maxL < 0:
					break
				if myChar == "1" :
					offX = 2
				else:
					offX = 0
					
				if flashloop == 0 and myChar == ":": 
					skipme = 1 # skip the colon this time, so the colon flashes every other second
				else:
					skipme = 0
					
				if skipme == 0 :
					text( draw, ( curX + offX , 1 ), myChar, fill="white", font=proportional( LCD_FONT ))
					
				if myChar == "." or myChar == ":" :
					curX = curX + 3
				else:
					curX = curX + 6
			# text( draw, ( tX, 0 ), compl, fill="white" )
		
		# pause for a bit
		
		time.sleep(1)

