#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import os
import sys
import time
import math
import threading
import numpy as np
import rrdtool
import pi3d
import importlib
from pkg_resources import resource_filename

from . import config
from .core import graphics
from .core import peripherals

try:
    unichr
except NameError:
    unichr = chr

# make 4M ramdisk for graph
if not os.path.isdir('/media/ramdisk'):
    os.popen('sudo mkdir /media/ramdisk')
    os.popen('sudo mount -t tmpfs -o size=4M tmpfs /media/ramdisk')

# os.chdir('/media/ramdisk')

# create rrd database for sensor logging
if not os.path.isfile('temperatures.rrd'):
    print('create rrd')
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


slides = []
subslides = dict()

for slidestring in config.slides:
    slides.append(importlib.import_module("shpi.slides." + slidestring))

for slidestring in config.subslides:
    subslides[slidestring] = importlib.import_module("shpi.subslides." + slidestring)

# bg_alpha = alphavalue of 2nd background, for transition effect
bg_alpha = 0

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

if config.START_MQTT_CLIENT:
    from .core import mqttclient
    try:
        mqttclient.init()
    except:
        pass

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
    except Exception as e:
        print('cannot start http server - error: ', e)


slide_offset = 0  # change by touch and slide
textchange = True # for reloading text 
sfg, sbg  = None, None  # sfg, sbg  two backrounds sprite for sliding
now = time.time()

def sensor_thread():
    global textchange, bg_alpha, sbg, sfg
    last_backlight_level = 0
    iFiles, nFi = get_files()
    pic_num = nFi - 1
    sfg = graphics.tex_load(iFiles[pic_num])
    nextsensorcheck = 0
    nexttm = 0

    while True:
        try:
            now = time.time()
            if now > nexttm:                 # change background
                nexttm = now + config.TMDELAY
                sbg = sfg
                sbg.positionZ(5)
                pic_num = (pic_num + 1) % nFi
                sfg = graphics.tex_load(iFiles[pic_num])
                bg_alpha = 0

            if peripherals.eg_object.alert:
                peripherals.alert()
            elif config.subslide == 'alert': # alert == 0
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
                print('set backlight:' + str(peripherals.eg_object.backlight_level))
                peripherals.controlbacklight(peripherals.eg_object.backlight_level)
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
                    peripherals.eg_object.act_temp, peripherals.eg_object.gputemp,
                    peripherals.eg_object.cputemp, peripherals.eg_object.atmega_temp,
                    sht_temp, bmp280_temp, peripherals.eg_object.mlxamb, peripherals.eg_object.mlxobj,
                    0.0, getattr(peripherals.eg_object, 'relais{}'.format(config.HEATINGRELAY)),
                    getattr(peripherals.eg_object, 'relais{}'.format(config.COOLINGRELAY)),
                    motion, peripherals.eg_object.humidity, peripherals.eg_object.a4)

                sys.stdout.write('\r')
                sys.stdout.write(temperatures_str)
                rrdtool.update(str('temperatures.rrd'), str(temperatures_str))
                sys.stdout.write(' i2c err:' + str(peripherals.eg_object.i2cerrorrate)+'% - ' + time.strftime("%H:%M") + ' ' )
                sys.stdout.flush()

                if config.SHOW_AIRQUALITY: #calculate rgb values for LED
                    redvalue = 255 if peripherals.eg_object.a4 > 600 else int(0.03 * peripherals.eg_object.a4)
                    greenvalue = 0 if peripherals.eg_object.a4 > 400 else int(0.02*(400 - peripherals.eg_object.a4))
                    peripherals.controlled([redvalue, greenvalue, 0])

        except Exception as e:
            print('error: {}'.format(e))
        time.sleep(0.2)

autoslide = time.time() + config.autoslidetm
peripherals.eg_object.slide = config.slide

t = threading.Thread(target=sensor_thread)
t.start()

movesfg = 0 # variable for parallax effect in sliding
time.sleep(1) #wait for running sensor_thread first time, to init all variables
f = 0
start = time.time()
while graphics.DISPLAY.loop_running():
    f += 1
    now = time.time()
    if f % 500 == 0:
        print('FPS={:.1f}'.format(f / (now - start)))
        f = 0
        start = now
    if not config.subslide:
        if bg_alpha < 1.0:                                              # fade to new background
            activity = True  # we calculate   more frames, when there is activity, otherwise we add sleep.time at end
            bg_alpha += 0.01
            sbg.draw()
            sfg.set_alpha(bg_alpha)
        sfg.draw()

    if config.SLIDE_PARALLAX and abs(movesfg) > 0:  # only do something if offset
        if abs(movesfg) < 1:  # needs to be > min move distance
            movesfg = 0
        else:
            movesfg -= math.copysign(0.3, movesfg)
            sfg.positionX(int(-movesfg))

    if peripherals.touched():  # and (peripherals.lasttouch + 0.4 > time.time()):  # check if touch is pressed, to detect sliding
        x, y = peripherals.get_touch()
        activity = True
        if ((x != 400) and peripherals.lastx):  # catch 0,0 -> 400,-240
            movex = (peripherals.lastx - x)
            if config.SLIDE_PARALLAX and abs(movex) > 20:
                movesfg = int( movex / 10)
                movesfg -= math.copysign(2,movesfg)
                sfg.positionX(-movesfg)

            if (abs(movex) > 30):  # calculate slider movement
                slide_offset = movex
                peripherals.touch_pressed = False  # to avoid clicking while sliding
    else:
        # autoslide demo mode
        if (len(config.autoslides) and peripherals.eg_object.backlight_level > 0 and
            peripherals.lasttouch + 10 < now and now > autoslide):
            movex += 10
            slide_offset = movex
            if movex > 200:
                autoslide = now + config.autoslidetm
        else:
            movex = 0
            peripherals.lastx = 0

    # start sliding when there is enough touchmovement
    if movex < -200 and peripherals.eg_object.slide > 0 and peripherals.lasttouch < (now - 0.1):
        peripherals.lastx = 0
        movex = 0
        peripherals.eg_object.slide -= 1
        sbg.set_alpha(0)
        if config.SLIDE_SHADOW:
            bg_alpha = 0
        slide_offset += 400

    if movex > 200 and peripherals.lasttouch < (now - 0.1):
        peripherals.lastx = 0
        movex = 0
        if peripherals.eg_object.slide < len(config.slides) - 1:
            peripherals.eg_object.slide += 1
        else:
            peripherals.eg_object.slide = 0

        if not peripherals.touched() and len(config.autoslideints):
            config.autoslideints = np.roll(config.autoslideints, 1)
            peripherals.eg_object.slide = config.autoslideints[0]
        else:
            sbg.set_alpha(0)
            if config.SLIDE_SHADOW:
                bg_alpha = 0
        slide_offset -= 400

    if config.subslide != None:
        activity = subslides[config.subslide].inloop(textchange, activity)
    elif -1 < peripherals.eg_object.slide < len(config.slides):
        activity, slide_offset = slides[peripherals.eg_object.slide].inloop(
            textchange, activity, slide_offset)

    textchange = False
    if not activity and (movesfg == 0) and (slide_offset == 0):
        time.sleep(0.05)
    activity = False
    if not os.path.exists("/media/ramdisk/screenshot.png"):
        pi3d.screenshot("/media/ramdisk/screenshot.png")

graphics.DISPLAY.destroy()
