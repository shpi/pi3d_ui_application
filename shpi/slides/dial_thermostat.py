#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from math import sin, cos, radians, atan2, degrees
from pkg_resources import resource_filename


import time
import os
import sys
import pi3d

from .. import config
from ..core import peripherals
from ..core import graphics
from ..core.dial import Dial

try:
    unichr
except NameError:
    unichr = chr

text = pi3d.PointText(graphics.pointFont, graphics.CAMERA,
                      max_chars=220, point_size=128)

if config.HEATINGRELAY != 0 or config.COOLINGRELAY != 0:
    offset_val_block = pi3d.TextBlock(0, -70, 0.1, 0.0, 15, data_obj=peripherals.eg_object,
            text_format=u"{:s}", attr="tempoffsetstr", size=0.5, spacing="F", space=0.05,
            colour=(1.0, 1.0, 1.0, 1.0), justify=0.5)
    text.add_text_block(offset_val_block)

    if peripherals.eg_object.tempoffset > 0:
        offset_val_block.colouring.set_colour([1, 0, 0])
    elif peripherals.eg_object.tempoffset < 0:
        offset_val_block.colouring.set_colour([0, 0, 1])
    else:
        offset_val_block.colouring.set_colour([1, 1, 1])

cloud = pi3d.TextBlock(-35, -117, 0.1, 0.0, 1, text_format=unichr(0xE002),
                           size=0.5, spacing="C", space=0.6, colour=(1, 1, 1, 0.9))
text.add_text_block(cloud)

if hasattr(peripherals.eg_object, 'pressure'):
    barometer = pi3d.TextBlock(15, -110, 0.1, 0.0, 2, text_format=unichr(
        0xE00B), size=0.6, spacing="F", space=0.05, colour=(1.0, 1.0, 1.0, 0.9))
    text.add_text_block(barometer)
    baroneedle = pi3d.Triangle(camera=graphics.CAMERA, corners=(
        (-3, 0, 0), (0, 15, 0), (3, 0, 0)), x=barometer.x+32, y=barometer.y - 12, z=0.1)
    baroneedle.set_shader(graphics.MATSH)

newtxt = pi3d.TextBlock(270, -180, 0.1, 0.0, 15, text_format=unichr(0xE001),
                        size=0.99, spacing="F", space=0.05, colour=(1.0, 1.0, 1.0, 1.0))
text.add_text_block(newtxt)
motiondetection = pi3d.TextBlock(290, -175, 0.1, 0.0, 15, text_format=unichr(
    0xE01C), size=0.79, spacing="F", space=0.05, colour=(1.0, 1.0, 1.0, 1.0))
text.add_text_block(motiondetection)

if config.HEATINGRELAY != 0:
    heating = pi3d.TextBlock(-20, -185, 0.1, 0.0, 15, text_format=unichr(
        0xE004), size=0.79, spacing="F", space=0.05, colour=(1.0, 1.0, 1.0, 1.0))
    text.add_text_block(heating)

if config.COOLINGRELAY != 0:
    newtxt = pi3d.TextBlock(20, -180, 0.1, 0.0, 15, text_format=unichr(0xE001),
                            size=0.99, spacing="F", space=0.05, colour=(1.0, 1.0, 1.0, 1.0))
    text.add_text_block(newtxt)
    cooling = pi3d.TextBlock(42, -182, 0.1, 0.0, 15, text_format=unichr(
        0xE029), size=0.79, spacing="F", space=0.05, colour=(1.0, 1.0, 1.0, 1.0))
    text.add_text_block(cooling)

dial = Dial(y = -20)
dial.check_touch(False,0)

def inloop(textchange=False, activity=False, offset=0):
    if peripherals.touched():
        offset = dial.check_touch(True, offset)
    elif dial.changed > 0:
        textchange = True

    if offset != 0:
        graphics.slider_change(dial.actval.text, offset)
        offset = graphics.slider_change(text.text, offset)
        graphics.slider_change(dial.dial, offset)
        if offset == 0:
            textchange = True

    if textchange:
        offset = dial.check_touch(False, offset)
        if peripherals.eg_object.tempoffset > 0:
            offset_val_block.colouring.set_colour([1, 0, 0])
        elif peripherals.eg_object.tempoffset < 0:
            offset_val_block.colouring.set_colour([0, 0, 1])
        else:
            offset_val_block.colouring.set_colour([1, 1, 1])

        red = (0.01 * (peripherals.eg_object.a4/4))
        if (red > 1):
            red = 1

        green = (0.01 * (120 - peripherals.eg_object.a4/4))
        if green < 0:
            green = 0
        if green > 1:
            green = 1

        cloud.colouring.set_colour([red, green, 0, 1.0])

        if config.COOLINGRELAY != 0:
            if getattr(peripherals.eg_object, 'relay{}'.format(config.COOLINGRELAY)):
                cooling.colouring.set_colour([0, 0, 1])
            else:
                cooling.colouring.set_colour([1, 1, 1])

        if config.HEATINGRELAY != 0:
            if getattr(peripherals.eg_object, 'relay{}'.format(config.HEATINGRELAY)):
                heating.colouring.set_colour([1, 1, 0])
            else:
                heating.colouring.set_colour([1, 1, 1])

        if hasattr(peripherals.eg_object, 'pressure'):
            normalizedpressure = (peripherals.eg_object.pressure - 950)
            if normalizedpressure < 0:
                normalizedpressure = 0
            if normalizedpressure > 100:
                normalizedpressure = 100
            green = 0.02 * (normalizedpressure)
            if green > 1:
                green = 1
            red = 0.02 * (100 - normalizedpressure)
            if red > 1:
                red = 1
            barometer.colouring.set_colour([red, green, 0, 1.0])
            baroneedle.set_material([red, green, 0])
            baroneedle.rotateToZ(100 - (normalizedpressure*2))
        text.regen()

    if hasattr(peripherals.eg_object, 'pressure') and offset == 0:
        baroneedle.draw()

    if (peripherals.eg_object.motion):
        motiondetection.colouring.set_colour([1, 0, 0])
    else:
        motiondetection.colouring.set_colour([1, 1, 1])

    if peripherals.touch_pressed:
        peripherals.touch_pressed = False

    dial.draw(offset)
    text.draw()

    return activity, offset
