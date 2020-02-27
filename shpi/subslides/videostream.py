#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import pi3d
from pkg_resources import resource_filename

from .. import config
from ..core import peripherals
from ..core import graphics

#sys.path.insert(1, os.path.join(sys.path[0], '..'))

font_path = resource_filename("shpi", "fonts/opensans.ttf")
str1 = pi3d.FixedString(font_path, 'Loading stream', font_size=32, background_color=(0,0,0,0),camera=graphics.CAMERA, shader=graphics.SHADER)
str1.sprite.position(0, 0, 0.1)
str2 = pi3d.FixedString(font_path, 'Touch to close stream.', font_size=22, background_color=(0,0,0,0), camera=graphics.CAMERA, shader=graphics.SHADER)
str2.sprite.position(0, -225, 0.1)



#videostream are opened from thermostat slide

def inloop(textchange = False,activity = False):

    str1.draw()
    str2.draw()
    if  peripherals.touch_pressed:
      peripherals.touch_pressed = False
      os.popen('killall omxplayer.bin')
      config.subslide = None

    return activity
