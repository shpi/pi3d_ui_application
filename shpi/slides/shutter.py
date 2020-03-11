#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import pi3d
import sys
import os

from .. import config
from ..core import peripherals
from ..core import graphics

try:
    unichr
except NameError:
    unichr = chr

text2 = pi3d.PointText(graphics.pointFontbig, graphics.CAMERA,
                       max_chars=35, point_size=256)  # slider2 Time & shutter

if config.SHUTTERUP != 0 or config.SHUTTERDOWN != 0:
    uhrzeit_block = pi3d.TextBlock(-70, 100, 0.1, 0.0, 15, justify=0.5,
                data_obj=peripherals.eg_object, attr="uhrzeit", text_format="{:s}",
                size=0.99, spacing="F", space=0.05, colour=(1.0, 1.0, 1.0, 1.0))
    text2.add_text_block(uhrzeit_block)

    shuttersymbol = pi3d.TextBlock(-100, -100, 0.1, 0.0, 15, text_format=unichr(0xE035),
                size=0.99, spacing="F", space=0.05, colour=(1.0, 1.0, 1.0, 1.0))
    text2.add_text_block(shuttersymbol)

    shutterDown = pi3d.TextBlock(300, -100, 0.1, 0.0, 1, text_format=unichr(0xE000),
                size=0.69, spacing="C", space=0.6, colour=(1, 1, 1, 0.8))
    text2.add_text_block(shutterDown)

    shutterUp = pi3d.TextBlock(-300, -100, 0.1, 180.0, 1, text_format=unichr(0xE000),
                size=0.69, spacing="C", space=0.6, colour=(1, 1, 1, 0.8))
    text2.add_text_block(shutterUp)
else:
    uhrzeit_block = pi3d.TextBlock(-280, 0, 0.1, 0.0, 15, data_obj=peripherals.eg_object,
                attr="uhrzeit", text_format="{:s}", size=0.99, spacing="F",
                space=0.05, colour=(1.0, 1.0, 1.0, 1.0))
    text2.add_text_block(uhrzeit_block)

shuttertimer = 0


def inloop(textchange=False, activity=False, offset=0):
    global shuttertimer
    if textchange:
        text2.regen()
    if shutterUp.y != -100 and shutterUp.colouring.colour[2] == 1:
        shutterUp.set_position(y=-100)
    if (shutterUp.colouring.colour[2] == 0):
        if shutterUp.y > 0:
            shutterUp.set_position(y=-100)
        shutterUp.set_position(y=(shutterUp.y+2))
        activity = True

    if shutterDown.y != -100 and shutterDown.colouring.colour[2] == 1:
        shutterDown.set_position(y=-100)
    if (shutterDown.colouring.colour[2] == 0):
        if shutterDown.y < -99:
            shutterDown.set_position(y=0)
        shutterDown.set_position(y=(shutterDown.y-2))
        activity = True

    if (shuttertimer > 0):
        if (shuttertimer > time.time()):
            peripherals.eg_object.uhrzeit = str(
                int(shuttertimer - time.time()))
            text2.regen()
        elif (shuttertimer < time.time()):
            shuttertimer = 0
            peripherals.eg_object.uhrzeit = time.strftime("%H:%M")
            text2.regen()
            peripherals.control_relay(config.SHUTTERDOWN, 0)
            peripherals.control_relay(config.SHUTTERUP, 0)
            shutterDown.colouring.set_colour([1, 1, 1])
            shutterUp.colouring.set_colour([1, 1, 1])

    if peripherals.touch_pressed:
        peripherals.touch_pressed = False
        if peripherals.clicked(shutterUp.x, shutterUp.y):
            peripherals.control_relay(config.SHUTTERDOWN, 0)
            peripherals.control_relay(config.SHUTTERUP, 1)
            shuttertimer = time.time() + config.SHUTTERTIMER
            shutterUp.colouring.set_colour([0, 1, 0])
            shutterDown.colouring.set_colour([1, 1, 1])
        elif peripherals.clicked(shutterDown.x, shutterDown.y):
            peripherals.control_relay(config.SHUTTERUP, 0)
            peripherals.control_relay(config.SHUTTERDOWN, 1)
            shuttertimer = time.time() + config.SHUTTERTIMER
            shutterUp.colouring.set_colour([1, 1, 1])
            shutterDown.colouring.set_colour([0, 1, 0])
        else:
            shuttertimer = 0
            peripherals.eg_object.uhrzeit = time.strftime("%H:%M")
            text2.regen()
            peripherals.control_relay(config.SHUTTERDOWN, 0)
            peripherals.control_relay(config.SHUTTERUP, 0)
            shutterUp.colouring.set_colour([1, 1, 1])
            shutterDown.colouring.set_colour([1, 1, 1])

    if offset != 0:
        offset = graphics.slider_change(text2.text, offset)
        if offset == 0:
            text2.regen()
    text2.draw()

    return activity, offset
