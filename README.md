# Demo pi3d_ui_application



Warning: Latest version needs ATmega firmware with CRC check. Please update atmega firmware. The software is in early development stage and is not fully documented so far. 

You can easily request functions by mailing lh@shpi.de


Create your own Slides simply by rename and modify one of our samples and add them in config.py.  

Headless Wifi Setup needs root rights.


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

*          http://ipshpi:port/?relay1     -> relay1:1;

*          http://ipshpi:port/?relay2     -> relay2:0;

*          http://ipshpi:port/?relay1=1   -> relay1:1;relay1>1;   SETS relay1 !

*          http://ipshpi:port/?led=255,255,255  ->   led>['255', '255', '255']; SETS RGB LED
          

#### MQTT Client
- [X] MQTT Client - start with START_MQTT_CLIENT = True in config.py

* published channels: <sup><sub>atmega_volt, d13, hwb, a0, a1, a2, a3, a4, a5, a7, atmega_temp, vent_rpm, vent_pwm, atmega_ram, buzzer, relay1current, mlxamb, mlxobj, bmp280_temp, pressure, lightlevel, sht_temp, humidity, motion, set_temp, backlight_level, gputemp, cputemp, act_temp, useddisk, load, freespace, wifistrength, ipaddress, led_red, led_green, led_blue, ssid, uhrzeit, relay1, relay2, relay3, lastmotion, max_backlight, usertext, usertextshow, alert</sub></sup>


* subscribed channels for remote control of SHPI (set/): <sup><sub>relay1, relay2, relay3, buzzer, d13, alert, max_backlight, set_temp, vent_pwm, led</sub></sup>
* USE: ON | OFF for relay1, relay2, relay3,buzzer d13, alert
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












