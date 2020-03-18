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

try:
    unichr
except NameError:
    unichr = chr

font_path = resource_filename("shpi", "fonts/opensans.ttf")
str1 = pi3d.FixedString(font_path, 'Loading stream', font_size=32, background_color=(0,0,0,0),
                        camera=graphics.CAMERA, shader=graphics.SHADER)
str1.sprite.position(0, 0, 0.1)
str2 = pi3d.FixedString(font_path, 'Touch to close stream.', font_size=22, background_color=(0,0,0,0),
                        camera=graphics.CAMERA, shader=graphics.SHADER)
str2.sprite.position(0, -225, 0.1)
str3 = pi3d.FixedString(font_path, unichr(0xE017), font_size=200, background_color=(0,0,0,0),
                        camera=graphics.CAMERA, shader=graphics.SHADER)
str3.sprite.position(320, -120, 0.0)
str5 = pi3d.FixedString(font_path, unichr(0xE017), font_size=200, background_color=(0,0,0,0),
                        color=(255,0,0,255), camera=graphics.CAMERA, shader=graphics.SHADER)
str5.sprite.position(320, -120, 0.0)
str4 = pi3d.FixedString(font_path, unichr(0xE026), font_size=200, background_color=(0,0,0,0),
                        camera=graphics.CAMERA, shader=graphics.SHADER)
str4.sprite.position(320, 50, 0.0)

def inloop(textchange=False, activity=False):
    str1.draw()
    str2.draw()
    str4.draw()

    if peripherals.touched():
        if peripherals.clicked(400,-150):
            str5.draw()
            #we deactivate speaker, while talking, to avaoid feedback and increase privacy for door intercoms
            os.popen('gpio -g write 27 0') #deactivate amplifier
            os.popen('i2cset -y 2 0x2A 0x93 0xFF') #deactivate vent
            os.popen("amixer -c 1 set 'PCM' 0%") #deactivate soundcard out
            os.popen("amixer -c 1 set 'Mic' 100%") #enable mic
    else:
        str3.draw()
        os.popen('gpio -g write 27 1') #deactivate amplifier
        os.popen('i2cset -y 2 0x2A 0x93 210') #deactivate vent
        os.popen("amixer -c 1 set 'PCM' 100%") #deactivate soundcard out
        os.popen("amixer -c 1 set 'Mic' 0%") #enable mic

    if (peripherals.check_touch_pressed() and (peripherals.lastx < 0)):        #only close if left side touched
        os.popen('killall nc') #warning just a test
        os.popen('killall ./videoplayer')
        os.popen('killall raspivid')
        config.subslide = None
    return activity
