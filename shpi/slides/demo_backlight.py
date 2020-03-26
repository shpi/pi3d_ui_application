#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from math import sin, cos, radians, atan2, degrees
from pkg_resources import resource_filename


import time
import os,subprocess
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
    def __init__(self, width=600, step=20, x = -300 , y = 0, thickness=50,
                min_t=1, max_t=31):

        self.width = width
        self.step = step
        self.thickness = thickness
        self.min_t = min_t
        self.max_t = max_t
        self.x = x
        self.y = y
        self.value = max_t
        tick_verts = []
        dial_verts = []
        bline_verts = []
        # first make tick vertices
        for x2 in range(0, self.width, self.step):
            tick_verts.extend([(x2 ,  -self.thickness/2, 0.2), (x2,self.thickness/2, 0.2)])
            bline_verts.append((x2,0,0.5))
        for x2 in range(self.x - 9, self.x + self.width+3, self.step):
            dial_verts.append((x2,0, 0.5))

        tex = pi3d.Texture(resource_filename("shpi", "sprites/color_gradient.jpg"))

        self.ticks = pi3d.PolygonLines(camera=graphics.CAMERA,x=self.x,y=self.y, vertices=tick_verts, strip=False, line_width=15)
        self.ticks.set_shader(graphics.MATSH)
        self.ticks.set_alpha(0.6)


        self.bline = pi3d.PolygonLines(camera=graphics.CAMERA, x=self.x,y=self.y,vertices=bline_verts, line_width=self.thickness)
        self.bline.set_textures([tex])
        self.bline.set_alpha(0.5)
        self.bline.set_shader(graphics.SHADER)
        self.bline.set_material((0.5,0.5,0.5))

        self.dial = pi3d.PolygonLines(camera=graphics.CAMERA, x=0, y=self.y, vertices=dial_verts, line_width=self.thickness+6)
        self.dial.set_alpha(0.4)
        self.dial.set_shader(graphics.MATSH)
        self.dial.set_material((0,0,0))


        self.actval = pi3d.PointText(graphics.pointFont, graphics.CAMERA, max_chars=8, point_size=100)
        self.temp_set = pi3d.TextBlock(self.x, self.y + 50, 0.1, 0.0, 2, text_format="00", size=0.6, spacing="F", space=0.02, colour=(0.0, 0.0, 0.0, 1), justify=1)
        self.actval.add_text_block(self.temp_set)


        self.dot2= pi3d.Disk(radius=int(self.thickness/2)+3, sides=30,x=self.x,y=self.y, z=0.2, rx=90, camera=graphics.CAMERA)
        self.dot2.set_shader(graphics.MATSH)
        self.dot2.set_material((1, 1, 1))
        self.dot2.set_alpha(0.8)

        self.valuex = 0

        self.changed = 0
 

    def check_touch(self,touched,offset):

           updateelements = []
           self.changed = 0

           if touched: 

            if ((self.valuex - 100 + self.x) < peripherals.xc and peripherals.xc  < (self.valuex + 100 + self.x) and
                (self.y - 100) < peripherals.yc and peripherals.yc  < (self.y + 100)):
                self.changed = 2

                peripherals.lastx, peripherals.lasty  = peripherals.xc,peripherals.yc # reset movex, to avoid sliding while changing dial
                offset = 0

                if self.valuex != peripherals.lastx - self.x:
                    self.valuex = peripherals.lastx - self.x
                    updateelements.append((self.bline,0.4))
                    peripherals.clicksound()
                    if self.valuex < 0:
                        self.valuex = 0
                    if self.valuex  > self.width:
                        self.valuex = self.width
                    self.dot2.position(self.valuex + self.x, self.y, 0.2)
                    updateelements.append((self.ticks,0.3))
                    self.temp_set.set_position(x=self.x + self.valuex)
                    peripherals.eg_object.max_backlight = int(self.min_t + (self.max_t - self.min_t) * (self.valuex / self.width))
                    self.temp_set.set_text(text_format="{:2d}".format(int(self.min_t + (self.max_t - self.min_t) * (self.valuex / self.width))))
                    self.actval.regen()

           else:

               if self.value !=  peripherals.eg_object.max_backlight:
                       self.value =  int(self.min_t +  (self.max_t - self.min_t) * (self.valuex / self.width))
                       file_path = resource_filename("shpi", "bin/backlight")
                       subprocess.run(["sudo",file_path,str(self.value)],stdin=None, stdout=None, stderr=None, close_fds=True)
                       #peripherals.eg_object.max_backlight = self.value


               if (self.valuex  !=  (self.width * (self.value - self.min_t))  / (self.max_t - self.min_t)):
                self.valuex = (self.width * (self.value - self.min_t))  / (self.max_t - self.min_t)
                self.dot2.position(self.valuex + self.x, self.y, 0.2)
                updateelements.append((self.ticks,0.3))




               self.temp_set.set_position(x=self.valuex + self.x)
               self.temp_set.set_text(text_format="{:2d}".format(int(self.value)))
               self.actval.regen()


           for (line_shape,z) in updateelements:
                    b = line_shape.buf[0]
                    v = b.array_buffer
                    cut_n = int((self.valuex / self.width) * len(v) / 4) * 4

                    if cut_n >= len(v):
                        cut_n = len(v) - 1
                    v[:cut_n, 2] = z  # set vis up to set point value
                    v[cut_n:,2] = -1.0
                    b.re_init()

           if self.changed > 1:

               self.bline.draw()
               self.changed = 1


           return offset

    def draw(self, offset):

        self.ticks.draw()
        self.dial.draw()
        self.dot2.draw()
        self.actval.draw()






dial = Dial()
dial.check_touch(False,0)

def inloop(textchange=False, activity=False, offset=0):

    if peripherals.touched():
        offset = dial.check_touch(True, offset)
    elif dial.changed > 0:
        textchange = True


    if offset != 0:
        offset = graphics.slider_change(dial.dial, offset)

        if offset == 0:
            textchange = True

    if textchange:
        offset = dial.check_touch(False, offset)


    dial.draw(offset)

    return activity, offset
