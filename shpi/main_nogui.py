#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import os
import sys
import time
import rrdtool
import pi3d
import importlib
import logging
#from pkg_resources import resource_filename

from . import config

# start logging NOW before anything else can log something
level = getattr(logging, config.LOG_LEVEL)
if config.LOG_FILE is not None:
    logging.basicConfig(filename=config.LOG_FILE, level=level)
else:
    logging.basicConfig(level=level) # defaults to screen

from .core import graphics
from .core import peripherals
"""
try:
    unichr
except NameError:
    unichr = chr
"""
# make 4M ramdisk for graph
if not os.path.isdir('/media/ramdisk'):
 os.popen('sudo mkdir /media/ramdisk')
 os.popen('sudo mount -t tmpfs -o size=4M tmpfs /media/ramdisk')

# os.chdir('/media/ramdisk')

def rrdcreate():
    os.popen('sudo rm temperatures.rrd')
    time.sleep(1)
    logging.debug('create rrd')
    rrdtool.create(
        "temperatures.rrd",
        "--step", "60",
        "DS:act_temp:GAUGE:120:-127:127",
        "DS:gpu:GAUGE:120:-127:127",
        "DS:cpu:GAUGE:120:-127:127",
        "DS:atmega:GAUGE:120:-127:127",
        "DS:sht:GAUGE:120:-127:127",
        "DS:bmp280:GAUGE:120:-127:127",
        "DS:mlxamb:GAUGE:120:-127:127",
        "DS:mlxobj:GAUGE:120:-127:127",
        "DS:ntc:GAUGE:120:-127:127",
        "DS:heating:GAUGE:120:0:1",
        "DS:cooling:GAUGE:120:0:1",
        "DS:movement:GAUGE:120:0:1",
        "DS:humidity:GAUGE:120:0:127",
        "DS:airquality:GAUGE:120:0:1023",
        "RRA:MAX:0.5:1:1500",
        "RRA:MAX:0.5:10:1500",
        "RRA:MAX:0.5:60:1500")

if not os.path.isfile('temperatures.rrd'):
  rrdcreate()

""" # are slides and subslides relevant in nogui?
slides = []
subslides = dict()

for slidestring in config.slides:
    slides.append(importlib.import_module('shpi.slides.' + slidestring))

for slidestring in config.subslides:
    subslides[slidestring] = importlib.import_module('shpi.subslides.' + slidestring)

# a = alphavalue of 2nd background, for transition effect
a = 0

def get_files():
    file_list = []
    extensions = ['.png', '.jpg', '.jpeg']
    for root, _dirnames, filenames in os.walk(resource_filename("shpi", "backgrounds")):
        for filename in filenames:
            ext = os.path.splitext(filename)[1].lower()
            if ext in extensions and not filename.startswith('.'):
                file_list.append(os.path.join(root, filename))
    # random.shuffle(file_list)
    return file_list, len(file_list)
"""
if config.START_MQTT_CLIENT:
    from .core import mqttclient
    try:
        mqttclient.init()
    except Exception as e:
        logging.warning("mqtt init failed: {}".format(e))

if config.START_HTTP_SERVER:
    try:
        # ThreadingHTTPServer for python 3.7
        from http.server import BaseHTTPRequestHandler, HTTPServer
    except:
        from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

    from .core.httpserver import ServerHandler

    try:
        littleserver = HTTPServer(("0.0.0.0", config.HTTP_PORT), ServerHandler)
        #littleserver = ThreadingHTTPServer(("0.0.0.0", 9000), ServerHandler)
        littleserver.timeout = 0.1
    except:
        logging.warning('cannot start http server - error')

now = time.time()
last_backlight_level = 0
nextsensorcheck = 0
nexttm = 0

while True:
    time.sleep(0.3)
    try:
        now = time.time()
        if now > nexttm:                                     # change background
            nexttm = now + config.TMDELAY

        if peripherals.eg_object.alert:
            peripherals.alert()
        elif config.subslide == 'alert':  # alert == 0
            peripherals.alert(0)
            config.subslide = None
            if config.START_MQTT_CLIENT:
                mqttclient.publish('alert', 'off')

        if config.BACKLIGHT_AUTO:
            if now < peripherals.eg_object.lastmotion + config.BACKLIGHT_AUTO:
                peripherals.eg_object.backlight_level = peripherals.eg_object.max_backlight
            else:
                peripherals.eg_object.backlight_level = config.MIN_BACKLIGHT

        if peripherals.eg_object.backlight_level != last_backlight_level:
            logging.info('set backlight:' + str(peripherals.eg_object.backlight_level))
            peripherals.control_backlight_level(peripherals.eg_object.backlight_level)
            last_backlight_level = peripherals.eg_object.backlight_level

        if config.START_HTTP_SERVER:
            littleserver.handle_request()

        if config.START_MQTT_CLIENT:
            mqttclient.publishall()

        peripherals.get_infrared()

        if (now > nextsensorcheck):
            peripherals.get_sensors()
            nextsensorcheck = now + config.SENSOR_TM

            if config.COOLINGRELAY != 0 and config.COOLINGRELAY == config.HEATINGRELAY:
                peripherals.coolingheating()
            else:
                if config.COOLINGRELAY != 0:
                    peripherals.cooling()
                if config.HEATINGRELAY != 0:
                    peripherals.heating()

            peripherals.get_status()
            textchange = True
            if hasattr(peripherals.eg_object, 'bmp280_temp'):
                bmp280_temp = peripherals.eg_object.bmp280_temp
            else:
                bmp280_temp = 0
            if hasattr(peripherals.eg_object, 'sht_temp'):
                sht_temp = peripherals.eg_object.sht_temp
            else:
                sht_temp = 0
            if now - peripherals.eg_object.lastmotion < 10: #only for rrd
                motion = 1
            else:
                motion = 0

            temperatures_str = 'N:{:.2f}:{:.2f}:{:.2f}:{:.2f}:{:.2f}:{:.2f}:{:.2f}:{:.2f}:{:.2f}:{:d}:{:d}:{:d}:{:.2f}:{:d}'.format(
                peripherals.eg_object.act_temp, peripherals.eg_object.gputemp, peripherals.eg_object.cputemp, peripherals.eg_object.atmega_temp,
                sht_temp, bmp280_temp, peripherals.eg_object.mlxamb, peripherals.eg_object.mlxobj, (0.0), getattr(
                    peripherals.eg_object, 'relay{}'.format(config.HEATINGRELAY)),
                getattr(peripherals.eg_object, 'relay{}'.format(config.COOLINGRELAY)), int(motion), peripherals.eg_object.humidity, peripherals.eg_object.a4)

            sys.stdout.write('\r') # not logged - maybe check against config.LOG_LEVEL
            sys.stdout.write(temperatures_str)
            rrdtool.update(str('temperatures.rrd'), str(temperatures_str))
            sys.stdout.write(' i2c err:' + str(peripherals.eg_object.i2cerrorrate)+'% - ' + time.strftime("%H:%M") + ' ' )
            sys.stdout.flush()

            if config.SHOW_AIRQUALITY: #calculate rgb values for LED
                redvalue = 255 if peripherals.eg_object.a4 > 600 else int(0.03 * peripherals.eg_object.a4)
                greenvalue = 0 if peripherals.eg_object.a4 > 400 else int(0.02*(400 - peripherals.eg_object.a4))
                peripherals.control_led([redvalue, greenvalue, 0])
        
    except Exception as e:
        logging.error("main loop failed: {}".format(e))