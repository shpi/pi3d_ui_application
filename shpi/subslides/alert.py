#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os,sys
import pi3d
from pkg_resources import resource_filename

from .. import config
from ..core import  peripherals
from ..core import graphics

#sys.path.insert(1, os.path.join(sys.path[0], '..'))

str1 = pi3d.FixedString(resource_filename("shpi", "fonts/opensans.ttf"), 'ALERT!',
            font_size=72, color=(255,0,0,255), background_color=(0,0,0,0),
            camera=graphics.CAMERA, shader=graphics.SHADER)
str1.sprite.position(0, 0, 0.1)

def inloop(textchange=False, activity=False):
    str1.draw()
    if  peripherals.check_touch_pressed():
        config.subslide = None
        peripherals.eg_object.alert = 0
        peripherals.alert(0)
    return activity
