# zero_main_application - Actual Development Status

Warning: Latest version needs ATmega firmware with CRC check. Please update atmega firmware. The software is in early development stage and is not fully documented so far. 

You can easily request functions by mailing lh@shpi.de


Create your own Slides simply by rename and modify one of our samples and add them in config.py.  

Headless Wifi Setup needs root rights.

Use "sudo crontab -e" or "sudo nano /etc/rc.local" for autostart

## Slides

- [X] Thermostat

*  Config: HYSTERESIS, COOLINGRELAY, HEATINGRELAY

- [X] Shutter

*  Config: shutterdown, shutterup

- [X] Amperemeter

- [X] Calendar

*  Config: ICALLINK


- [X] ATmega / Sensor Status

- [X] Statistics RRD

- [X] Live Graph

- [X] Floorplan Demo with example Window / Door / Movement areas

- [ ] Lightswitch

- [X] Remote Switch HTTP

## Subslides (non slideable)

- [X] Videostream

- [X] Intercom

- [X] Alert


## Configuration

- [X] Seperate config file: config.py

- [ ] Webserver Config Page

- [X] Headless WIFI Setup (accessible over settings slide)

## Connectivity

#### HTTP Server
All vars from eg_object (core/peripherals.py) are accessible.

- [X] HTTP Server

*          http://ipshpi:port/?relais1     -> relais1:1;

*          http://ipshpi:port/?relais2     -> relais2:0;

*          http://ipshpi:port/?relais1=1   -> relais1:1;relais1>1;   SETS Relais1 !

*          http://ipshpi:port/?led=255,255,255  ->   led>['255', '255', '255']; SETS RGB LED
          

#### MQTT Client
- [X] MQTT Client - start with START_MQTT_CLIENT = True in config.py

* published channels: <sup><sub>atmega_volt, d13, hwb, a0, a1, a2, a3, a4, a5, a7, atmega_temp, vent_rpm, vent_pwm, atmega_ram, buzzer, relais1current, mlxamb, mlxobj, bmp280_temp, pressure, lightlevel, sht_temp, humidity, motion, set_temp, backlight_level, gputemp, cputemp, act_temp, useddisk, load, freespace, wifistrength, ipaddress, led_red, led_green, led_blue, ssid, uhrzeit, relais1, relais2, relais3, lastmotion, max_backlight, usertext, usertextshow, alert</sub></sup>


* subscribed channels for remote control of SHPI (set/): <sup><sub>relais1, relais2, relais3, buzzer, d13, alert, max_backlight, set_temp, vent_pwm, led</sub></sup>
* USE: ON | OFF for relais1, relais2, relais3,buzzer d13, alert
* USE: 1 .. 31 for max_backlight
* USE: 0.0 .. 88.5 for set_temp
* USE: 0 .. 255 for vent_pwm
* USE: 255,255,255 for led

- [ ] Apple Home Kit (testing)

- [ ] Config Files for Openhab, Loxone, FHEM, IP Symcon

- [ ] Bluetooth Sensor Broadcasting ?

## Controlling Functions

- [X] Cooling

- [X] Heating

- [X] Alert

- [ ] Vent

- [ ] Mail, SMS, WhatsApp, HTTP
## Hardware (Drivers, Interface)


- [X] Display with Touchdriver (touchdriver.py in other demos for Desktop)

- [X] ATmega 32u4 I2C Firmware

- [X] CULFW Implementation for CC1101

- [X] Backlight Control

- [X] Reduce Power consumption: GPIO Drive Strength, disable HDMI


- [ ] Xiaomi Bluetooth Sensors











