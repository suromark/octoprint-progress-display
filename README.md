# octoprint-progress-display
A display for Octoprint progress data

## stuff to set up
These are the steps I did in the Raspberry Pi terminal to get the display to work. No guarantees...

*just to get the system up-to-date* 

sudo apt-get update

*need to install some python stuff later* 

sudo apt-get install python-pip

*enable the SPI interface in the configuration, if not yet available* 

sudo raspi-config 

*let the pi user access the SPI port* 

sudo usermod -a -G spi,gpio pi

*components for the display* 

sudo apt-get install build-essential python-dev python-pip libfreetype6-dev libjpeg-dev

sudo -H pip install --upgrade --ignore-installed pip setuptools

*the actual driver software* 

sudo -H pip install --upgrade luma.led_matrix

*clone the LED matrix driver sources* 

git clone https://github.com/rm-hull/luma.led_matrix.git

*run a demo display for a 4-module board*

python /home/pi/luma.led_matrix/examples/matrix_demo.py --cascaded 4 --block-orientation -90

*now copy the ma_progreport.py script into /home/pi/*

*add a call to /etc/rc.local so it runs as a separate thread on boot*

sudo nano /etc/rc.local

*insert before the last "exit 0" this line:*

/home/pi/ma_progreport.py &

*then save and reboot*

@TODO: wiring schematics!
