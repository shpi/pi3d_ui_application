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
imgsize = (250, 250) #The size of the image

image = Image.new('RGB', imgsize) #Create the image



for y in range(imgsize[1]):
    for x in range(imgsize[0]):

        distanceToCenter = math.sqrt((x - imgsize[0]/2) ** 2 + (y - imgsize[1]/2) ** 2)
        distanceToCenter = float(distanceToCenter) / (math.sqrt(2) * imgsize[0]/2)

        x1 = (x - imgsize[0]/2) 
        y1 = (y - imgsize[1]/2)
        degree = degrees(atan2(x1, y1))
        
        (r,g,b) = colorsys.hsv_to_rgb(degree/360, distanceToCenter, 1)
        r = int(r*255)
        g = int(g*255)
        b = int(b*255)
        image.putpixel((x, y), (r,g,b))


tex = pi3d.Texture(image) 

shader = pi3d.Shader("uv_flat")
sprite = pi3d.ImageSprite(tex, shader, w=250.0, h=250.0, z=0.1)



def inloop(textchange=False, activity=False, offset=0):

    #if peripherals.touched():
    sprite.draw()
    if offset != 0:
        offset = graphics.slider_change(box.mrb, offset)

        if offset == 0:
            textchange = True

    #if textchange:



    return activity, offset
