#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import os
import sys
import time
import math
import threading
import rrdtool
import pi3d
import importlib
import logging
from pkg_resources import resource_filename

from . import config

# start logging NOW before anything else can log something
log_level = getattr(logging, config.LOG_LEVEL)
if config.LOG_FILE is not None:
    logging.basicConfig(filename=config.LOG_FILE, level=log_level)
else:
    logging.basicConfig(level=log_level)  # defaults to screen

from .core import peripherals #i.e. these imports MUST happen after logging starts!

if config.SHOW_WIFISTATUS:
   from .core import wifistatus
   wifistatus = wifistatus.WifiStatus()

if config.SHOW_SLIDESTATUS:
   from .core import slidestatus
   slidestatus = slidestatus.SlideStatus()


if config.GUI:
    from .core import graphics

try:
    unichr
except NameError:
    unichr = chr


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


def sensor_thread():
    global textchange, bg_alpha, sbg, sfg
    nextsensorcheck = 0
    if config.GUI:
        last_backlight_level = 0
        iFiles, nFi = get_files()
        pic_num = nFi - 1
        sfg = graphics.tex_load(iFiles[pic_num])
        nexttm = 0

    while True:
        try:
            now = time.time()
            if config.GUI and now > nexttm:           # change background
                nexttm = now + config.TMDELAY
                sbg = sfg
                sbg.positionZ(5)
                pic_num = (pic_num + 1) % nFi
                sfg = graphics.tex_load(iFiles[pic_num])
                bg_alpha = 0

            if peripherals.eg_object.alert:
                peripherals.alert()
            elif config.subslide == 'alert':  # alert == 0
                peripherals.alert(0)
                config.subslide = None
                if config.START_MQTT_CLIENT:
                    mqttclient.publish('alert', 'off')

            if config.GUI:
                if config.BACKLIGHT_AUTO:
                    if now < peripherals.eg_object.lastmotion + config.BACKLIGHT_AUTO:
                        peripherals.eg_object.backlight_level = peripherals.eg_object.max_backlight
                    else:
                        peripherals.eg_object.backlight_level = config.MIN_BACKLIGHT

                if peripherals.eg_object.backlight_level != last_backlight_level:
                    logging.info('set backlight:' +
                                str(peripherals.eg_object.backlight_level))
                    peripherals.control_backlight_level(
                        peripherals.eg_object.backlight_level)
                    last_backlight_level = peripherals.eg_object.backlight_level

            if config.START_HTTP_SERVER:
                littleserver.handle_request()

           

            peripherals.get_infrared()

            for attr in peripherals.control_list:
                val = peripherals.control_list[attr]
                peripherals.do_control(attr, val)
                if config.SHOW_SLIDESTATUS and attr == 'slide':
                   slidestatus.update(peripherals.eg_object.slide)
            peripherals.control_list = {}

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

                if config.START_MQTT_CLIENT:
                    mqttclient.publishall()

                if config.SHOW_WIFISTATUS:
                    wifistatus.update()


                textchange = True
                if hasattr(peripherals.eg_object, 'bmp280_temp'):
                    bmp280_temp = peripherals.eg_object.bmp280_temp
                else:
                    bmp280_temp = 0

                if hasattr(peripherals.eg_object, 'sht_temp'):
                    sht_temp = peripherals.eg_object.sht_temp
                else:
                    sht_temp = 0

                if now - peripherals.eg_object.lastmotion < 10:  # only for rrd
                    motion = 1
                else:
                    motion = 0

                temperatures_str = 'N:{:.2f}:{:.2f}:{:.2f}:{:.2f}:{:.2f}:{:.2f}:{:.2f}:{:.2f}:{:.2f}:{:d}:{:d}:{:d}:{:.2f}:{:d}'.format(
                    peripherals.eg_object.act_temp, peripherals.eg_object.gputemp,
                    peripherals.eg_object.cputemp, peripherals.eg_object.atmega_temp,
                    sht_temp, bmp280_temp, peripherals.eg_object.mlxamb, peripherals.eg_object.mlxobj,
                    0.0, getattr(peripherals.eg_object,'relay{}'.format(config.HEATINGRELAY)),
                    getattr(peripherals.eg_object,'relay{}'.format(config.COOLINGRELAY)),
                    motion, peripherals.eg_object.humidity, peripherals.eg_object.a4)

                rrdtool.update(str('temperatures.rrd'), str(temperatures_str))


                """ not logged - maybe this is because of some other issue with stdout
                TODO check if logging would be OK.
                log_level determined at start (int val of config.LOG_LEVEL)
                """
                if log_level <= logging.DEBUG: # only output if log_level is debug
                    sys.stdout.write('\r')
                    sys.stdout.write(temperatures_str)
                    
                    sys.stdout.write(
                        ' i2c err:' + str(peripherals.eg_object.i2cerrorrate)+'% - ' + time.strftime("%H:%M") + ' ')
                    sys.stdout.flush()

                if config.SHOW_AIRQUALITY:  # calculate rgb values for LED
                    redvalue = 255 if peripherals.eg_object.a4 > 600 else int(0.03 * peripherals.eg_object.a4)
                    greenvalue = 0 if peripherals.eg_object.a4 > 400 else int(0.02*(400 - peripherals.eg_object.a4))
                    #peripherals.control_led([redvalue, greenvalue, 0])
                    peripherals.control_led_color(peripherals.COLOR_RED, redvalue)
                    peripherals.control_led_color(peripherals.COLOR_GREEN, greenvalue)
                    peripherals.control_led_color(peripherals.COLOR_BLUE, 0)



        except Exception as e:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            line_number = exception_traceback.tb_lineno
            logging.error('sensor_thread error: {}'.format(e))
            logging.error('error in line: {}'.format(line_number))
            time.sleep(0.2)


# make 4M ramdisk for graph
"""if not os.path.isdir('/media/ramdisk'):
    os.popen('sudo mkdir /media/ramdisk')
    os.popen('sudo mount -t tmpfs -o size=4M tmpfs /media/ramdisk')"""

# os.chdir('/media/ramdisk')

# create rrd database for sensor logging
if not os.path.isfile('temperatures.rrd'):
    logging.info('create rrd')
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

if config.GUI:
    slides = []
    subslides = dict()

    for slidestring in config.slides:
        try:
            slides.append(importlib.import_module("shpi.slides." + slidestring))
        except:
            logging.error(f"error loading slide: " + slidestring)
            pass

    for slidestring in config.subslides:
        subslides[slidestring] = importlib.import_module(
            "shpi.subslides." + slidestring)

    # bg_alpha = alphavalue of 2nd background, for transition effect
    bg_alpha = 0

if config.START_MQTT_CLIENT:
    from .core import mqttclient
    try:
        mqttclient.init()
    except Exception as e:
        logging.warning(f"cannot start mqtt client - error: {e}")

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
        logging.warning(f"cannot start http server - error: {e}")

slide_offset = 0  # change by touch and slide
textchange = True  # for reloading text
sfg, sbg = None, None  # sfg, sbg  two backrounds sprite for sliding
now = time.time()

autoslide = time.time() + config.autoslidetm
peripherals.eg_object.slide = config.slide

t = threading.Thread(target=sensor_thread)
t.start()

if config.GUI:
    movesfg = 0  # variable for parallax effect in sliding
    time.sleep(1)  # wait for running sensor_thread first time, to init all variables
    f = 0
    start = time.time()
    while graphics.DISPLAY.loop_running(): #TODO way of stopping loop
        f += 1
        now = time.time()
        if f % 500 == 0:
            logging.debug('FPS={:.1f}'.format(f / (now - start)))
            f = 0
            start = now
        if config.subslide is None:
            if bg_alpha < 1.0:   # fade to new background
                activity = True  # we calculate more frames, when there is activity, otherwise we add sleep.time at end
                bg_alpha += 0.01
                sbg.draw()
                sfg.set_alpha(bg_alpha)
            sfg.draw()

        # only do something if offset
        if config.SLIDE_PARALLAX and abs(movesfg) > 0:
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
                    movesfg = int(movex / 10)
                    movesfg -= math.copysign(2, movesfg)
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
        if (movex < -200 and peripherals.eg_object.slide > 0 and
                            peripherals.lasttouch < (now - 0.1)):
            peripherals.lastx = 0
            movex = 0
            peripherals.eg_object.slide -= 1

            if config.SHOW_SLIDESTATUS:
               slidestatus.update(peripherals.eg_object.slide)

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

            if not peripherals.touched() and len(config.autoslideints) > 0:
                config.autoslideints = config.autoslideints[1:] + \
                    config.autoslideints[0:1]
                peripherals.eg_object.slide = config.autoslideints[0]
            else:
                sbg.set_alpha(0)
                if config.SLIDE_SHADOW:
                    bg_alpha = 0
            slide_offset -= 400

            if config.SHOW_SLIDESTATUS:
               slidestatus.update(peripherals.eg_object.slide)




        if config.subslide is not None:
            activity = subslides[config.subslide].inloop(textchange, activity)
        elif -1 < peripherals.eg_object.slide < len(config.slides):
            activity, slide_offset = slides[peripherals.eg_object.slide].inloop(
                textchange, activity, slide_offset)
            if config.SHOW_SLIDESTATUS:
               slidestatus.draw()



        if config.SHOW_WIFISTATUS:
            wifistatus.draw()

        textchange = False
        if not activity and (movesfg == 0) and (slide_offset == 0):
            time.sleep(0.05)
        activity = False

        if not os.path.exists("/dev/shm/screenshot.png"):
            pi3d.screenshot("/dev/shm/screenshot.png")

else:
    while True: #TODO way of stopping loop 
        time.sleep(0.5)

if config.GUI:
    graphics.DISPLAY.destroy() #TODO way of stopping loop so this has some effect
