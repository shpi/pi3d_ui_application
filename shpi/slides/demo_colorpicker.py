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
imgsize = (440, 440) #The size of the image

image = Image.new('RGB', imgsize) #Create the image

convertRadiansToDegrees = 180.0 / 3.14159265359


for y in range(imgsize[1]):
    for x in range(imgsize[0]):

        distanceToCenter = math.sqrt((x - imgsize[0]/2) ** 2 + (y - imgsize[1]/2) ** 2) / (imgsize[0]/2)

        x1 = (x - imgsize[0]/2) 
        y1 = (imgsize[1]/2-y)
        
        resultInDegrees = atan2(x1,y1) * convertRadiansToDegrees + 180

        (r,g,b) = colorsys.hsv_to_rgb(resultInDegrees/360, distanceToCenter, 1)
        
        r = int(r*255)
        g = int(g*255)
        b = int(b*255)
        image.putpixel((x, y), (r,g,b))


tex = pi3d.Texture(image) 

shader = pi3d.Shader("uv_flat")
#sprite = pi3d.ImageSprite(tex, shader, w=250.0, h=250.0, z=0.1)
dot = pi3d.Disk(radius=220, sides=50,x=0,y=0, z=0.2, rx=90, camera=graphics.CAMERA)
dot.set_textures([tex])
dot.set_shader(shader)

dot2 = pi3d.Disk(radius=222, sides=50,x=0,y=0, z=0.3, rx=90, camera=graphics.CAMERA)
dot2.set_shader(graphics.MATSH)
dot2.set_material((0,0,0))
dot2.set_alpha(0.8)

dot3 = pi3d.Disk(radius=30, sides=50,x=0,y=0, z=0.1, rx=90, camera=graphics.CAMERA)
dot3.set_shader(graphics.MATSH)
dot3.set_material((0,0,0))

dot4 = pi3d.Disk(radius=31, sides=50,x=0,y=0, z=0.15, rx=90, camera=graphics.CAMERA)
dot4.set_shader(graphics.MATSH)
dot4.set_material((0,0,0))



def inloop(textchange=False, activity=False, offset=0):
    global convertRadiansToDegrees

    if peripherals.touch_pressed:
        peripherals.touch_pressed = False

        distanceToCenter = math.sqrt((peripherals.lastx) ** 2 + (peripherals.lasty) ** 2)


        if distanceToCenter < 300:

         resultInDegrees = atan2(peripherals.lastx,peripherals.lasty) * convertRadiansToDegrees + 180



         if distanceToCenter > 220:
               distanceToCenter = 220
               peripherals.lastx = 220 * sin(radians(degrees(atan2(peripherals.lastx,peripherals.lasty)))) 
               peripherals.lasty = 220 * cos(radians(degrees(atan2(peripherals.lastx,peripherals.lasty))))


         distanceToCenter3 = float(distanceToCenter) / (220)
         if distanceToCenter3 > 1:
            distanceToCenter3 = 1
        

         dot3.position(x=peripherals.lastx,y=peripherals.lasty,z=0.1)
         dot4.position(x=peripherals.lastx,y=peripherals.lasty,z=0.15)

         (r,g,b) = colorsys.hsv_to_rgb(resultInDegrees/360, distanceToCenter3, 1)
       
         peripherals.control_led([int(r*255),int(g*255),int(b*255)])
         dot3.set_material((r,g,b))

    dot2.draw()
    dot.draw()
    dot4.draw()
    dot3.draw()

    if offset != 0:
        #offset = graphics.slider_change(box.mrb, offset)

        if offset == 0:
            textchange = True

    #if textchange:



    return activity, offset
