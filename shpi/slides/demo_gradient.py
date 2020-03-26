#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from math import sin, cos, radians, atan2, degrees
from pkg_resources import resource_filename


import time
import os,subprocess
import sys
import pi3d

from math import pi

from pi3d.Buffer import Buffer
from pi3d.util import Utility
from pi3d.Shape import Shape


from .. import config
from ..core import peripherals
from ..core import graphics


from PIL import Image
import math
import colorsys
imgsize = (64, 32) #The size of the image

image = Image.new('RGB', imgsize) #Create the image

def interpolate(f_color, t_color, interval):
    det_color =[(t - f) / interval for f , t in zip(f_color, t_color)]
    for i in range(interval):
        yield [round(f + det * i) for f, det in zip(f_color, det_color)]


f = (13, 255, 154)
t = (4, 128, 30)


for i, color in enumerate(interpolate(f, t, imgsize[0])):

    
       for y in range(imgsize[1]):
         image.putpixel((i,y), tuple(color))


tex = pi3d.Texture(image) 

shader = pi3d.Shader("uv_flat")
sprite = pi3d.ImageSprite(tex, shader,x=0,y=0, w=780.0, h=200.0, z=0.1)



def inloop(textchange=False, activity=False, offset=0):
    global convertRadiansToDegrees

    #if peripherals.touch_pressed:
    #    peripherals.touch_pressed = False


    sprite.draw()

    if offset != 0:
        #offset = graphics.slider_change(box.mrb, offset)

        if offset == 0:
            textchange = True

    #if textchange:



    return activity, offset
