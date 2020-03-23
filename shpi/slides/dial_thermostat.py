#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from math import sin, cos, radians, atan2, degrees
from pkg_resources import resource_filename


import time
import os
import sys
import pi3d

from .. import config
from ..core import peripherals
from ..core import graphics

try:
    unichr
except NameError:
    unichr = chr






class Dial(object):
    def __init__(self, angle_fr=-140, angle_to=145, step=8, x = 0 , y = 0, outer=250, inner=180,
                min_t=15, max_t=30, shader=None, camera=None):

        self.angle_fr = angle_fr
        self.angle_to = angle_to
        self.step = step
        self.outer = outer
        self.inner = inner
        self.mid = (outer + inner) / 2
        self.min_t = min_t
        self.max_t = max_t
        self.x = x
        self.y = y

        tick_verts = []
        dial_verts = []
        # first make tick vertices
        for x2 in range(self.angle_fr, self.angle_to, self.step):
            (s, c) = (sin(radians(x2)), cos(radians(x2))) # re-use for brevity below
            tick_verts.extend([(self.inner * s, self.inner * c, 0.2),
                                (self.outer * s, self.outer * c, 0.2)])
            dial_verts.append((self.mid * s, self.mid * c, 2.0))


        tex = pi3d.Texture(resource_filename("shpi", "sprites/color_gradient.jpg"))

        self.ticks = pi3d.PolygonLines(camera=graphics.CAMERA,x=self.x,y=self.y, vertices=tick_verts, strip=False, line_width=8)
        self.ticks.set_shader(graphics.MATSH)
        self.ticks.set_alpha(0.8)

        self.sensorticks = pi3d.PolygonLines(camera=graphics.CAMERA, x=self.x,y=self.y,vertices=tick_verts, line_width=8, strip=False)
        self.sensorticks.set_shader(graphics.MATSH)

        self.bline = pi3d.PolygonLines(camera=graphics.CAMERA, x=self.x,y=self.y,vertices=dial_verts, line_width=80)
        self.bline.set_textures([tex])
        self.bline.set_alpha(0.8)
        self.bline.set_shader(graphics.SHADER)
        self.bline.set_material((0.5,0.5,0.5))

        self.trian = pi3d.Triangle(camera=graphics.CAMERA, x=self.x, y=self.y, z = 0.1, corners=(
                (-15, (self.inner - 20),0), (0, self.inner+5,0), (15, (self.inner - 20),0)))
        self.trian.set_shader(graphics.MATSH)
        self.trian.set_material((0.3,0.1,0))
        self.trian.set_alpha(1)


        self.dial = pi3d.PolygonLines(camera=graphics.CAMERA, x=self.x, y=self.y, vertices=dial_verts, line_width=84)
        self.dial.set_alpha(0.4)
        self.dial.set_shader(graphics.MATSH)
        self.dial.set_material((0,0,0))

        self.actval = pi3d.PointText(graphics.pointFont, graphics.CAMERA, max_chars=14, point_size=100) 
        self.temp_block = pi3d.TextBlock(self.x, self.y + 10, 0.1, 0.0, 6, justify=0.6, text_format="0°", size=0.99,
                    spacing="F", space=0.02, colour=(1.0, 1.0, 1.0, 1.0))
        self.actval.add_text_block(self.temp_block)


        self.temp_set = pi3d.TextBlock(0, self.inner-30, 0.1, 0, 4, text_format="{:4.1f}".format(peripherals.eg_object.set_temp), size=0.35, spacing="F", space=0.02,
            colour=(1.0, 1.0, 1.0, 1), justify=0.6)
        self.actval.add_text_block(self.temp_set)

        self.dot1= pi3d.Disk(radius=130, sides=30,x=self.x,y=self.y, z=2, rx=90, camera=graphics.CAMERA)
        self.dot1.set_shader(graphics.MATSH)
        self.dot1.set_material((0, 0, 0))
        self.dot1.set_alpha(0.4)


        self.dot2= pi3d.Disk(radius=30, sides=20,x=self.x,y=self.y, z=0.1, rx=90, camera=graphics.CAMERA)
        self.dot2.set_shader(graphics.MATSH)
        self.dot2.set_material((1, 1, 1))
        self.dot2_alpha = 1.0


        self.value = peripherals.eg_object.set_temp
        self.sensorvalue = peripherals.eg_object.act_temp
        self.degree = (self.angle_fr +  (self.angle_to - self.angle_fr) * (self.value - self.min_t)
                                                            / (self.max_t - self.min_t))
        self.trian.rotateToZ(-self.degree+self.step)



        if self.sensorvalue < self.min_t:
           self.sensorvalue = self.min_t
        if self.sensorvalue > self.max_t:
           self.sensorvalue = self.max_t
        self.sensordegree = (self.angle_fr +  (self.angle_to - self.angle_fr) * (self.sensorvalue - self.min_t)
                                                            / (self.max_t - self.min_t))
        
        self.x1 = self.mid * sin(radians(self.degree)) + self.x
        self.y1 = self.mid * cos(radians(self.degree)) + self.y
        self.changed = 0
        self.dot2.position(self.x1, self.y1, 0.5)
        self.dot2_alpha = 1.0
        self.temp_set.set_position(x= ((self.inner-33) * sin(radians(self.degree-self.step)) + self.x), 
                                   y= ((self.inner-33) * cos(radians(self.degree-self.step)) + self.y),
                                   rot=-self.degree+self.step)

        

    def check_touch(self,touched,offset):

           updateelements = []
           self.changed = 0
           if touched: # and (abs(offset) < 30): 
            
            if ((self.x1 - 100) < peripherals.xc and peripherals.xc  < (self.x1 + 100) and
                (self.y1 - 100) < peripherals.yc and peripherals.yc  < (self.y1 + 100)):
                self.changed = 2
                 
                peripherals.lastx, peripherals.lasty  = peripherals.xc,peripherals.yc # reset movex, to avoid sliding while changing dial
                offset = 0

                if self.degree != int(degrees(atan2(peripherals.lastx - self.x, peripherals.lasty - self.y))):
                    self.degree = int(degrees(atan2(peripherals.lastx - self.x, peripherals.lasty - self.y)))
                    self.changed = 2
                    updateelements.append((self.bline, (None, 0.3, None, -1.0)))
                    peripherals.clicksound()
                    if self.degree < self.angle_fr:
                        self.degree = self.angle_fr
                    if self.degree > self.angle_to:
                        self.degree = self.angle_to
                    self.trian.rotateToZ(-self.degree+self.step)

                    self.temp_set.set_position(x= ((self.inner-33) * sin(radians(self.degree-self.step)) + self.x), 
                                   y= ((self.inner-33) * cos(radians(self.degree-self.step)) + self.y),
                                   rot=-self.degree+self.step)








                    peripherals.eg_object.set_temp = (self.min_t + (self.degree - self.angle_fr)
                             / (self.angle_to - self.angle_fr) * (self.max_t - self.min_t))
                    self.x1 = self.mid * sin(radians(self.degree)) + self.x
                    self.y1 = self.mid * cos(radians(self.degree)) + self.y


           else:

               if (self.value != peripherals.eg_object.set_temp) or (self.sensorvalue != peripherals.eg_object.act_temp) :
                self.changed = 1

                self.value = peripherals.eg_object.set_temp 
                self.degree = (self.angle_fr +  (self.angle_to - self.angle_fr) * (self.value - self.min_t)
                                                            / (self.max_t - self.min_t))
                self.x1 = self.mid * sin(radians(self.degree)) + self.x
                self.y1 = self.mid * cos(radians(self.degree)) + self.y
                self.sensorvalue = peripherals.eg_object.act_temp
                if self.dot2_alpha < 0:
                    self.temp_block.set_text(text_format="{:4.1f}°".format(self.sensorvalue))
                self.actval.regen()
                if self.sensorvalue < self.min_t:
                    self.sensorvalue = self.min_t
                if self.sensorvalue > self.max_t:
                    self.sensorvalue = self.max_t
                self.sensordegree = (self.angle_fr +  (self.angle_to - self.angle_fr) * (self.sensorvalue - self.min_t)
                                                            / (self.max_t - self.min_t))
                updateelements.append((self.ticks, (0.3, -1.0, 0.3, -1.0)))
                self.trian.rotateToZ(-self.degree+self.step)
                self.temp_set.set_position(x= ((self.inner-33) * sin(radians(self.degree-self.step)) + self.x), 
                                   y= ((self.inner-33) * cos(radians(self.degree-self.step)) + self.y),
                                   rot=-self.degree+self.step)
                self.temp_set.set_text(text_format="{:4.1f}".format(peripherals.eg_object.set_temp))
        


                if  self.value > self.sensorvalue:
                    self.ticks.set_material((1, 0 , 0))
                    updateelements.append((self.sensorticks, (0.4, None, None, -1.0)))

                else:
                    self.ticks.set_material((0,0,1))
                    updateelements.append((self.sensorticks, (0.4, None, 0.4, -1.0)))

                
 

           #updateelements.append((self.ticks, (-1.0, -1.0, 0.1, -1.0)))
           #updateelements.append((self.sensorticks, (0.2, None, None, -1.0)))
           #updateelements.append((self.dial, (-1.0, -1.0, 0.1, 0.1)))
           #updateelements.append((self.sensorticks, (0.2, None, None, -1.0)))
           #updateelements.append((self.dial, (-1.0, -1.0, 0.1, 0.1)))
      

           for (line_shape, z) in updateelements:
                    b = line_shape.buf[0]
                    v = b.array_buffer
                    cut_n = int((self.degree - self.angle_fr) / (self.angle_to - self.angle_fr) * len(v) / 4) * 4
                    if cut_n >= len(v):
                        cut_n = len(v) - 1
                    cut_s = int((self.sensordegree - self.angle_fr) / (self.angle_to - self.angle_fr) * len(v) / 4) * 4
                    if cut_s >= len(v):
                        cut_s = len(v) - 1
                    v[:, 2] = z[3]           # all set to the 'otherwise' value
                    if z[0] is not None:
                        v[:cut_s, 2] = z[0]  # set visibility up to sensor value
                    if z[1] is not None:
                        v[:cut_n, 2] = z[1]  # set vis up to set point value
                    if z[2] is not None:     # set between cut_n and cut_s
                        if cut_s > cut_n:
                            v[cut_n:cut_s, 2] = z[2]
                        else:
                            v[cut_s:cut_n, 2] = z[2]
                    b.re_init()
                    #b.set_material(rgb)

           

           if self.changed > 1:
               self.temp_block.set_text(text_format="{:4.1f}°".format(peripherals.eg_object.set_temp))
               self.temp_set.set_text(text_format="{:4.1f}".format(peripherals.eg_object.set_temp))
               rgbval = round((self.degree - self.angle_fr) / (self.angle_to - self.angle_fr), 2) # rgbval 0.0 - 1.0

               self.temp_block.colouring.set_colour([rgbval, 0, 1 - rgbval])
               self.dot2.position(self.x1, self.y1, 0.5)
               self.dot2_alpha = 1.0
               self.ticks_alpha = 0.0
               self.bline.draw()
               self.changed = 1
               self.actval.regen()


           return offset
               
            

    def draw(self, offset):
        self.dot1.draw()
        if self.dot2_alpha >= 0.0:
            self.dot2_alpha -= 0.1
            self.dot2.set_alpha(self.dot2_alpha)
            if abs(offset) < 30:
                self.dot2.draw()
            if self.dot2_alpha < 0:
                self.temp_block.set_text(text_format="{:4.1f}°".format(self.sensorvalue))
                self.temp_block.colouring.set_colour([1, 1, 1])
                self.actval.regen()
                self.ticks_alpha = 0
        else:
            if self.ticks_alpha <= 1.0:
                self.ticks_alpha += 0.05
                self.ticks.set_alpha(self.ticks_alpha)
                if self.ticks_alpha >= 1.0:
                    self.ticks_alpha = 0.1
            if abs(offset) < 30:
                self.sensorticks.draw()
                self.ticks.draw()
                self.trian.draw()

        self.dial.draw()
        self.actval.draw()






text = pi3d.PointText(graphics.pointFont, graphics.CAMERA,
                      max_chars=220, point_size=128)


if config.HEATINGRELAY != 0 or config.COOLINGRELAY != 0:
    offset_temp_block = pi3d.TextBlock(0, -70, 0.1, 0.0, 15, data_obj=peripherals.eg_object, text_format=u"{:s}", attr="tempoffsetstr",
                                       size=0.5, spacing="F", space=0.05, colour=(1.0, 1.0, 1.0, 1.0), justify=0.5)
    text.add_text_block(offset_temp_block)

    if peripherals.eg_object.tempoffset > 0:
        offset_temp_block.colouring.set_colour([1, 0, 0])
    elif peripherals.eg_object.tempoffset < 0:
        offset_temp_block.colouring.set_colour([0, 0, 1])
    else:
        offset_temp_block.colouring.set_colour([1, 1, 1])

cloud = pi3d.TextBlock(-35, -117, 0.1, 0.0, 1, text_format=unichr(0xE002),
                           size=0.5, spacing="C", space=0.6, colour=(1, 1, 1, 0.9))
text.add_text_block(cloud)

if hasattr(peripherals.eg_object, 'pressure'):
    barometer = pi3d.TextBlock(15, -110, 0.1, 0.0, 2, text_format=unichr(
        0xE00B), size=0.6, spacing="F", space=0.05, colour=(1.0, 1.0, 1.0, 0.9))
    text.add_text_block(barometer)
    baroneedle = pi3d.Triangle(camera=graphics.CAMERA, corners=(
        (-3, 0, 0), (0, 15, 0), (3, 0, 0)), x=barometer.x+32, y=barometer.y - 12, z=0.1)
    baroneedle.set_shader(graphics.MATSH)

newtxt = pi3d.TextBlock(270, -180, 0.1, 0.0, 15, text_format=unichr(0xE001),
                        size=0.99, spacing="F", space=0.05, colour=(1.0, 1.0, 1.0, 1.0))
text.add_text_block(newtxt)
motiondetection = pi3d.TextBlock(290, -175, 0.1, 0.0, 15, text_format=unichr(
    0xE01C), size=0.79, spacing="F", space=0.05, colour=(1.0, 1.0, 1.0, 1.0))
text.add_text_block(motiondetection)

if config.HEATINGRELAY != 0:
    heating = pi3d.TextBlock(-20, -185, 0.1, 0.0, 15, text_format=unichr(
        0xE004), size=0.79, spacing="F", space=0.05, colour=(1.0, 1.0, 1.0, 1.0))
    text.add_text_block(heating)

if config.COOLINGRELAY != 0:
    newtxt = pi3d.TextBlock(20, -180, 0.1, 0.0, 15, text_format=unichr(0xE001),
                            size=0.99, spacing="F", space=0.05, colour=(1.0, 1.0, 1.0, 1.0))
    text.add_text_block(newtxt)
    cooling = pi3d.TextBlock(42, -182, 0.1, 0.0, 15, text_format=unichr(
        0xE029), size=0.79, spacing="F", space=0.05, colour=(1.0, 1.0, 1.0, 1.0))
    text.add_text_block(cooling)


dial = Dial(y = -20)
dial.check_touch(False,0)

def inloop(textchange=False, activity=False, offset=0):

    if peripherals.touched():
        offset = dial.check_touch(True, offset)
    elif dial.changed > 0:
        textchange = True
 

    if offset != 0:
        graphics.slider_change(dial.actval.text, offset)
        offset = graphics.slider_change(text.text, offset)
        graphics.slider_change(dial.dial, offset)

        if offset == 0:
            textchange = True

    if textchange:
        offset = dial.check_touch(False, offset)
        if peripherals.eg_object.tempoffset > 0:
            offset_temp_block.colouring.set_colour([1, 0, 0])
        elif peripherals.eg_object.tempoffset < 0:
            offset_temp_block.colouring.set_colour([0, 0, 1])
        else:
            offset_temp_block.colouring.set_colour([1, 1, 1])

        red = (0.01 * (peripherals.eg_object.a4/4))
        if (red > 1):
            red = 1

        green = (0.01 * (120 - peripherals.eg_object.a4/4))
        if green < 0:
            green = 0
        if green > 1:
            green = 1

        cloud.colouring.set_colour([red, green, 0, 1.0])

        if config.COOLINGRELAY != 0:
            if getattr(peripherals.eg_object, 'relay{}'.format(config.COOLINGRELAY)):
                cooling.colouring.set_colour([0, 0, 1])
            else:
                cooling.colouring.set_colour([1, 1, 1])

        if config.HEATINGRELAY != 0:
            if getattr(peripherals.eg_object, 'relay{}'.format(config.HEATINGRELAY)):
                heating.colouring.set_colour([1, 1, 0])
            else:
                heating.colouring.set_colour([1, 1, 1])

        if hasattr(peripherals.eg_object, 'pressure'):
            normalizedpressure = (peripherals.eg_object.pressure - 950)
            if normalizedpressure < 0:
                normalizedpressure = 0
            if normalizedpressure > 100:
                normalizedpressure = 100
            green = 0.02 * (normalizedpressure)
            if green > 1:
                green = 1
            red = 0.02 * (100 - normalizedpressure)
            if red > 1:
                red = 1
            barometer.colouring.set_colour([red, green, 0, 1.0])
            baroneedle.set_material([red, green, 0])
            baroneedle.rotateToZ(100 - (normalizedpressure*2))
        text.regen()

    if hasattr(peripherals.eg_object, 'pressure') and offset == 0:
        baroneedle.draw()

    if (peripherals.eg_object.motion):
        motiondetection.colouring.set_colour([1, 0, 0])
    else:
        motiondetection.colouring.set_colour([1, 1, 1])

    if peripherals.touch_pressed:
        peripherals.touch_pressed = False



    dial.draw(offset)
    text.draw()
    
    return activity, offset
