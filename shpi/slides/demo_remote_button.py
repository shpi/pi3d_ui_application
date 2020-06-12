#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import pi3d
import json
import logging

from .. import config  # TODO need this import?
from ..core import peripherals
from ..core import graphics
from ..core import mqttclient

try:
    import urllib.request as urlopen
except:
    from urllib2 import urlopen

try:
    unichr
except NameError:
    unichr = chr

text = pi3d.PointText(graphics.pointFont, graphics.CAMERA,
                      max_chars=35, point_size=128)
# also big font possible, higher resolution
text2 = pi3d.PointText(graphics.pointFontbig,
                       graphics.CAMERA, max_chars=35, point_size=256)

# look for graphics in core/graphics.py  0xE00F -> light,   0xE001 -> circle
httpbutton = pi3d.TextBlock(0, 0, 0.1, 0.0, 1, text_format=unichr(
    0xE00F), size=0.99, spacing="C", space=0.6, colour=(1, 1, 1, 1))
circle = pi3d.TextBlock(-5, 15, 0.1, 0.0, 1, text_format=unichr(0xE001),
                        size=0.99, spacing="C", space=0.6, colour=(1, 1, 1, 1))

text.add_text_block(httpbutton)
text2.add_text_block(circle)
httpbutton.status = 'unknown'  # on init status is unknown


def get_button_status():
    try:
        a = urlopen('http://blabla/relay1')
    except:
        logging.error('Error httpbutton')
        httpbutton.status = 'error'
    else:
        if a.getcode() == 200:
            content = a.read()
            if content == 'ON':
                httpbutton.status = 'ON'
                httpbutton.colouring.set_colour([0, 1, 0])
            elif content == 'OFF':
                httpbutton.status = 'OFF'
                httpbutton.colouring.set_colour([1, 0, 0])

# solution for shelly:
#     status = json.loads(content)
#     logging.info(status)
#     if status['ison']:
#        httpbutton.status = 'ON'
#        httpbutton.colouring.set_colour([0,1,0])
#     else:
#        httpbutton.status = 'OFF'
#        httpbutton.colouring.set_colour([1,0,0])


def inloop(textchange=False, activity=False, offset=0):
    if textchange:
        text.regen()
        text2.regen()

    if httpbutton.status == 'unknown':
        get_button_status()
    if httpbutton.status == 'error':
        httpbutton.colouring.set_colour([0, 0, 1])
    peripherals.check_touch_pressed()
    if peripherals.clicked(httpbutton.x, httpbutton.y):
        if httpbutton.status == 'OFF':
            try:
                _a = urlopen('http://blabla/relay1=1')
            except:
                logging.error('error httpbutton')
            else:
                # if a.getcode() == 200:  #checks http status code 200 = OK
                # we change color of button to green
                httpbutton.colouring.set_colour([0, 1, 0])
                httpbutton.status = 'ON'

                # we could also check response content
                # if a.read() == 'OK':       check content
        elif httpbutton.status == 'ON':
            try:
                _a = urlopen('http://blabla/relay1=0')
            except:
                logging.error('error httpbutton')
            else:
                # if a.getcode() == 200:  #checks http status code 200 = OK
                # we change color of button to red
                httpbutton.colouring.set_colour([1, 0, 0])
                httpbutton.status = 'OFF'
    if offset != 0:
        graphics.slider_change(text2.text, offset)
        offset = graphics.slider_change(text.text, offset)
        if offset == 0:
            httpbutton.status = 'unknown'
            text.regen()
            text2.regen()

    text.draw()
    text2.draw()

    return activity, offset
