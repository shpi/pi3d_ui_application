# zero_main_application - Actual Development Status

You can easily request functions by mailing lh@shpi.de

## Slides

- [X] Thermostat

*  Config: HYSTERESIS, coolingrelay, heatingrelay

- [X] Shutter

*  Config: shutterdown, shutterup

- [X] Amperemeter

- [X] Calendar

*  Config: icallink


- [X] ATmega / Sensor Status

- [X] Statistics RRD

- [ ] Live Graph (testing, in other demos)

- [ ] 2D Visu (testing, in other demos)

- [ ] Lightswitch

- [ ] Remote Switch for IP Symcon, Openhab, FHEM, Shelly, Loxone




## Configuration

- [X] Seperate config file: config.py

- [ ] Webserver Config Page

- [X] Headless WIFI Setup (accessible over settings slide)

## Connectivity

- [X] HTTP Server

### - [X] MQTT Client - start with startmqttclient = 1 in config.py

* published channels: <sup><sub>atmega_volt, d13, hwb, a0, a1, a2, a3, a4, a5, a7, atmega_temp, vent_rpm, vent_pwm, atmega_ram, buzzer, relais1current, mlxamb, mlxobj, bmp280_temp, pressure, lightlevel, sht_temp, humidity, motion, set_temp, backlight_level, gputemp, cputemp, act_temp, useddisk, load, freespace, wifistrength, ipaddress, led_red, led_green, led_blue, ssid, uhrzeit, relais1, relais2, relais3, lastmotion, max_backlight, usertext, usertextshow, alert</sub></sup>


* subscribed channels for remote control of SHPI (set/): <sup><sub>relais1, relais2, relais3, buzzer, d13, alert, max_backlight, set_temp, vent_pwm, led</sub></sup>


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











