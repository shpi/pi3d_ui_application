#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os,sys

import pi3d

sys.path.insert(1, os.path.join(sys.path[0], '..'))

import core.peripherals as peripherals
import core.graphics as graphics
import config




str1 = pi3d.FixedString(config.installpath + 'fonts/opensans.ttf', 'Loading stream', font_size=32, background_color=(0,0,0,0),camera=graphics.CAMERA, shader=graphics.SHADER)
str1.sprite.position(0, 0, 0.1)
str2 = pi3d.FixedString(config.installpath + 'fonts/opensans.ttf', 'Touch to close stream.', font_size=22, background_color=(0,0,0,0), camera=graphics.CAMERA, shader=graphics.SHADER)
str2.sprite.position(0, -225, 0.1)
str3 = pi3d.FixedString(config.installpath + 'fonts/opensans.ttf', chr(0xE017), font_size=200, background_color=(0,0,0,0), camera=graphics.CAMERA, shader=graphics.SHADER)
str3.sprite.position(320, -120, 0.0)
str5 = pi3d.FixedString(config.installpath + 'fonts/opensans.ttf', chr(0xE017), font_size=200, background_color=(0,0,0,0), color=(255,0,0,255), camera=graphics.CAMERA, shader=graphics.SHADER)
str5.sprite.position(320, -120, 0.0)
str4 = pi3d.FixedString(config.installpath + 'fonts/opensans.ttf', chr(0xE026), font_size=200, background_color=(0,0,0,0), camera=graphics.CAMERA, shader=graphics.SHADER)
str4.sprite.position(320, 50, 0.0)

def inloop(textchange = False,activity = False):

    str1.draw()
    str2.draw()
    str4.draw()

    if peripherals.touched():

      if peripherals.clicked(400,-150):
        str5.draw()

        #we deactivate speaker, while talking, to avaoid feedback and increase privacy for door intercoms
        #os.popen('amixer set Master 0%')
        #os.popen('amixer set Capture 100%')

    else:
      str3.draw()
      #os.popen('amixer set Master 100%')
      #os.popen('amixer set Capture 0%')
    if (peripherals.touch_pressed and (peripherals.lastx < 0)):        #only close if left side touched
      peripherals.touch_pressed = False
      os.popen('killall nc') #warning just a test
      os.popen('killall ./videoplayer')
      os.popen('killall omxplayer.bin')
      os.popen('killall raspivid')
      config.subslide = None

