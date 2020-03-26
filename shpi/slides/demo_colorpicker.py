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



def interpolate(f_color, t_color, interval):
    det_color =[(t - f) / interval for f , t in zip(f_color, t_color)]
    for i in range(interval):
        yield [round(f + det * i) for f, det in zip(f_color, det_color)]


def gradient(f_color = (0,0,0), t_color = (0,0,0), size = 16, vertical = False):
 image = Image.new('RGB', (size,size)) #Create the image
 for x, color in enumerate(interpolate(f_color, t_color, size)):

       for y in range(size):
         if vertical: image.putpixel((x,y), tuple(color))
         else:        image.putpixel((y,x), tuple(color))

 return image



def blackgradient(size= 255,gradient_magnitude=1.):
    
    gradient = Image.new('L', (2,size), color=0xFF)
    for x in range(size):
        # gradient.putpixel((x, 0), 255-x)
        #for y in range(size):
       gradient.putpixel((0,x), int(255 * (1 - gradient_magnitude * float(x)/size)))
       gradient.putpixel((1,x), int(255 * (1 - gradient_magnitude * float(x)/size)))
    #alpha = gradient.resize(im.size)
    black_im = Image.new('RGBA', (2,size), color=0) # i.e. black
    black_im.putalpha(gradient)
    return black_im



tex = pi3d.Texture(blackgradient())
rect = pi3d.Sprite(camera=graphics.CAMERA,x=300,y=0,w=100,h=440,z=0.2)
rect.set_material((1.0, 1.0, 1.0))
sprite = pi3d.ImageSprite(tex, graphics.SHADER,x=300,y=0, w=100.0, h=440.0, z=0.1)





imgsize = (32, 32) #The size of the image
image = Image.new('RGB', imgsize) #Create the image

convertRadiansToDegrees = 180.0 / 3.14159265359


for y in range(imgsize[1]):
    
    for x in range(imgsize[0]):


         x1 = (x - imgsize[0]/2)
         y1 = (imgsize[1]/2-y)

         distanceToCenter = math.sqrt(x1 ** 2 + y1 ** 2) / (imgsize[0]/2)

         #if distanceToCenter < 1: result in little mipmap error
        
         resultInDegrees = atan2(x1,y1) * convertRadiansToDegrees + 180

         (r,g,b) = colorsys.hsv_to_rgb(resultInDegrees/360, distanceToCenter, 1)
        
         r = int(r*255)
         g = int(g*255)
         b = int(b*255)
         image.putpixel((x, y), (r,g,b))

#image.save("/home/pi/circulargradient.png")

tex2 = pi3d.Texture(image) 

dot = pi3d.Disk(radius=220, sides=50,x=0,y=0, z=0.2, rx=90, camera=graphics.CAMERA)
dot.set_textures([tex2])
dot.set_shader(graphics.SHADER)

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
    global convertRadiansToDegrees, sprite

    #if peripherals.touch_pressed:
    #    peripherals.touch_pressed = False
    if peripherals.touched():
     if ((dot4.x() - 100) < peripherals.xc and peripherals.xc  < (dot4.x() + 100) and
                (dot4.y() - 100) < peripherals.yc and peripherals.yc  < (dot4.y() + 100)):

         distanceToCenter = math.sqrt((peripherals.xc) ** 2 + (peripherals.yc) ** 2)



         resultInDegrees = atan2(peripherals.xc,peripherals.yc) * convertRadiansToDegrees + 180



         if distanceToCenter > 220:
               distanceToCenter = 220
               radian = radians(degrees(atan2(peripherals.xc,peripherals.yc)))
               peripherals.lastx = 220 * sin(radian) 
               peripherals.lasty = 220 * cos(radian)

         else:
              peripherals.lasty = peripherals.yc
              peripherals.lastx = peripherals.xc


         dot3.position(x=peripherals.lastx,y=peripherals.lasty,z=0.1)
         dot4.position(x=peripherals.lastx,y=peripherals.lasty,z=0.15)



         distanceToCenter3 = float(distanceToCenter) / (220)
         if distanceToCenter3 > 1:
            distanceToCenter3 = 1

         (r,g,b) = colorsys.hsv_to_rgb(resultInDegrees/360, distanceToCenter3, 1)

         dot3.set_material((r,g,b))
         rect.set_material((r,g,b))




         (r,g,b) = (int(r*255),int(g*255),int(b*255))


         #tex.update_ndarray(gradient(t_color=(r,g,b)), 0)
         #tex.im = tex._img_to_array(gradient(t_color=(r,g,b)))
         #tex = pi3d.Texture(gradient(t_color=(r,g,b)))
         #sprite.set_textures([pi3d.Texture(gradient(t_color=(r,g,b)))])
         #tex._load_opengl()



         if [r,g,b] != peripherals.eg_object.led:
           peripherals.control_led([r,g,b])

         # idea to speed it up
         #if r != peripherals.eg_object.led_red:
         # peripherals.control_led_color(peripherals.COLOR_RED,r)
         # peripherals.eg_object.led_red = r

         #if g != peripherals.eg_object.led_green:
         # peripherals.control_led_color(peripherals.COLOR_GREEN, g)
         # peripherals.eg_object.led_red = g

         #if b != peripherals.eg_object.led_blue:
         # peripherals.control_led_color(peripherals.COLOR_BLUE, b)
         # peripherals.eg_object.led_red = b


    #sprite.draw()
    dot2.draw()
    dot.draw()
    dot4.draw()
    dot3.draw()
    rect.draw()
    sprite.draw()

    if offset != 0:
        #offset = graphics.slider_change(box.mrb, offset)

        if offset == 0:
            textchange = True

    #if textchange:



    return activity, offset
