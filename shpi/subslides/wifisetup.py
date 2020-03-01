#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import pi3d
from pkg_resources import resource_filename

from .. import config
from ..core import peripherals
from ..core import graphics
from ..core import iwlist

#sys.path.insert(1, os.path.join(sys.path[0], '..'))

try:
    unichr
except NameError:
    unichr = chr

font_path = resource_filename("shpi", "fonts/opensans.ttf")
controlx= pi3d.FixedString(font_path, unichr(0xE01E), font_size=65,shadow_radius=4, 
                        background_color=(0,0,0,0), color= (255,255,255,255),
                        camera=graphics.CAMERA, shader=graphics.SHADER, f_type='SMOOTH')
controlx.sprite.position(335, 196, 1)

wifinetworkstext = pi3d.FixedString(font_path, 'Choose your WIFI-network:' , font_size=42, shadow_radius=4,justify='L', background_color=(0,0,0,30), color= (255,255,255,255),camera=graphics.CAMERA, shader=graphics.SHADER, f_type='SMOOTH')
wifinetworkstext.sprite.position(0, 200, 1)
wifinetworks = None
selectednetwork = None

def inloop(x=0, y=0, touch_pressed=False, textchange=False, activity=False):
    global wifinetworks, selectednetwork
    wifinetworkstext.draw()
    controlx.draw()
    if wifinetworks is None: # only runs once as this block creates 
        actnetwork = 0
        wifinetworks = iwlist.scan()
 
        for network in wifinetworks:
            if network['essid'] == '':
                network['essid'] = 'hidden'
            wifinetworks[actnetwork]['string'] = pi3d.FixedString(font_path,
                            'SSID: {}, Enc:{}  Ch:{}'.format(
                                network['essid'], network['enc'], network['ch']),
                            font_size=32, shadow_radius=4, justify='L',
                            background_color=(0,0,0,30), color= (255,255,255,255),
                            camera=graphics.CAMERA, shader=graphics.SHADER, f_type='SMOOTH')
            wifinetworks[actnetwork]['string'].sprite.position(0, (100 - (actnetwork*80)), 1)
            actnetwork += 1
    else:
        for network in wifinetworks:
            network['string'].draw()
        if peripherals.touch_pressed:
            peripherals.touch_pressed = False
            activity = True
            if peripherals.clicked(335, 196):
                config.subslide = None
                wifinetworks = None
           
            else:
                selectednetwork = abs(int((peripherals.lasty - 100) / 80))
                if -1 <  selectednetwork  <  len(wifinetworks):
                    peripherals.eg_object.usertextshow = 'Please enter WIFI password.'
                    peripherals.eg_object.usertext = ''
                    config.subslide = 'wifikeyboard'

    return activity