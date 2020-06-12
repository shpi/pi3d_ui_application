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

do_setup = True
#videostream are opened from thermostat slide
def inloop(textchange=False, activity=False):
    global do_setup
    if do_setup:
        try:
            os.popen('killall omxplayer.bin')
        except:
            pass
        os.popen(
            "omxplayer --threshold 0.5  --display 4 rtsp://username:pass@192.168.1.5:554/mpeg4cif --win '0 0 800 450'")
        # loading time depends on keyframes in stream, only h264 recommended!
        do_setup = False
    str1.draw()
    str2.draw()
    if  peripherals.check_touch_pressed():
        os.popen('killall omxplayer.bin')
        config.subslide = None
        do_setup = True

    return activity
