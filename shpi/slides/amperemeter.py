#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import pi3d
import logging
from pkg_resources import resource_filename

from .. import config
from ..core import peripherals
from ..core import graphics

FACTOR = 5000.0 / 1024.0 / 185.0

text5 = pi3d.PointText(graphics.pointFont, graphics.CAMERA,
                       max_chars=20, point_size=64)  # slider5 Ammeter
currents = pi3d.TextBlock(-350, 100, 0.1, 0.0, 15, data_obj=peripherals.eg_object, attr="relay1current", text_format="{:2.1f}A", size=0.99, spacing="F",
                          space=0.05, colour=(1.0, 1.0, 1.0, 1.0))
text5.add_text_block(currents)

file_path = resource_filename("shpi", "sprites/amperemeter.png")
amperemeter = pi3d.ImageSprite(file_path, shader=graphics.SHADER, camera=graphics.CAMERA,
                               w=400, h=400, x=0, y=0, z=2.0)
ampereneedle = pi3d.Lines(camera=graphics.CAMERA, vertices=((0, 0, 0), (0, 160, 0)),
                          material=(1.0, 0.3, 0.0), line_width=5, x=0.0, y=-70.0, z=1.0)
ampereneedle.set_shader(graphics.MATSH)


def inloop(textchange=False, activity=False, offset=0):
    if offset != 0:
        offset = graphics.slider_change(amperemeter, offset)
    else:
        ampereneedle.rotateToZ(50 - peripherals.eg_object.relay1current * 20)
        ampereneedle.draw()

    amperemeter.draw()
    text5.draw()

    if peripherals.ADDR_32U4 != 0:
     try:
        peripherals.eg_object.relay1current = FACTOR * \
            (peripherals.read_two_bytes(peripherals.READ_RELAY1CURRENT) - 1)
        text5.regen()
     except Exception as e:
        logging.error('error: {}'.format(e))

    return activity, offset
