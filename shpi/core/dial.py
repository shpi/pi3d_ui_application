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
    def __init__(self, angle_fr=-140, angle_to=140, step=8, x=0, y=0,
        outer=250, inner=180, min_v=15, max_v=30, text_format="{:4.1f}°",
        set_field="set_temp", act_field="act_temp", shader=None, camera=None):

        self.angle_fr = angle_fr
        self.angle_to = angle_to
        self.step = step
        self.outer = outer
        self.inner = inner
        self.mid = (outer + inner) / 2
        self.min_v = min_v
        self.max_v = max_v
        self.x = x
        self.y = y
        self.set_field = set_field
        self.act_field = act_field
        self.text_format = text_format

        tick_verts = []
        dial_verts = []
        # first make tick vertices
        for x2 in range(self.angle_fr, self.angle_to, self.step):
            (s, c) = (sin(radians(x2)), cos(radians(x2))) # re-use for brevity below
            tick_verts.extend([(self.inner * s, self.inner * c, 0.1),
                                (self.outer * s, self.outer * c, 0.1)])
            dial_verts.append((self.mid * s, self.mid * c, 2.0))

        tex = pi3d.Texture(resource_filename("shpi", "sprites/color_gradient.jpg"))

        self.ticks = pi3d.PolygonLines(camera=graphics.CAMERA, x=self.x, y=self.y,
                vertices=tick_verts, strip=False, line_width=8)
        self.ticks.set_shader(graphics.MATSH)
        self.ticks.set_alpha(0.8)

        self.sensorticks = pi3d.PolygonLines(camera=graphics.CAMERA, x=self.x,
                y=self.y, vertices=tick_verts, line_width=8, strip=False)
        self.sensorticks.set_shader(graphics.MATSH)

        self.bline = pi3d.PolygonLines(camera=graphics.CAMERA, x=self.x, y=self.y,
                vertices=dial_verts, line_width=80)
        self.bline.set_textures([tex])
        self.bline.set_alpha(0.8)
        self.bline.set_shader(graphics.SHADER)
        self.bline.set_material((0.5,0.5,0.5))

        self.trian = pi3d.Triangle(camera=graphics.CAMERA, x=self.x, y=self.y,
                z = 0.1, corners=((-15, self.inner - 20, 0),
                                  (0, self.inner + 5, 0),
                                  (15, self.inner - 20, 0)))
        self.trian.set_shader(graphics.MATSH)
        self.trian.set_material((0.3,0.1,0))
        self.trian.set_alpha(1)

        self.dial = pi3d.PolygonLines(camera=graphics.CAMERA, x=self.x, y=self.y,
                vertices=dial_verts, line_width=84)
        self.dial.set_alpha(0.2)
        self.dial.set_shader(graphics.MATSH)
        self.dial.set_material((0,0,0))

        self.actval = pi3d.PointText(graphics.pointFont, graphics.CAMERA,
                max_chars=23, point_size=100) 
        self.val_block = pi3d.TextBlock(self.x, self.y + 10, 0.1, 0.0, 11,
                justify=0.6, text_format=text_format, size=0.99, spacing="F",
                space=0.02, colour=(1.0, 1.0, 1.0, 1.0))
        self.actval.add_text_block(self.val_block)

        self.value = getattr(peripherals.eg_object, self.set_field)
        self.sensorvalue = getattr(peripherals.eg_object, self.act_field)

        self.set_block = pi3d.TextBlock(0, self.inner - 30, 0.1, 0, 11,
                text_format=self.text_format.format(self.value),
                size=0.35, spacing="F", space=0.02, colour=(1.0, 1.0, 1.0, 1), justify=0.6)
        self.actval.add_text_block(self.set_block)

        self.dot1= pi3d.Disk(radius=130, sides=30, x=self.x, y=self.y, z=2, rx=90,
                camera=graphics.CAMERA)
        self.dot1.set_shader(graphics.MATSH)
        self.dot1.set_material((0, 0, 0))
        self.dot1.set_alpha(0.4)

        self.dot2= pi3d.Disk(radius=30, sides=20,x=self.x,y=self.y, z=0.1, rx=90,
                camera=graphics.CAMERA)
        self.dot2.set_shader(graphics.MATSH)
        self.dot2.set_material((1, 1, 1))
        self.dot2_alpha = 1.0

        self.degree = (self.angle_fr
                +  (self.angle_to - self.angle_fr) * (self.value - self.min_v)
                / (self.max_v - self.min_v))
        self.trian.rotateToZ(-self.degree + self.step)

        if self.sensorvalue < self.min_v:
           self.sensorvalue = self.min_v
        if self.sensorvalue > self.max_v:
           self.sensorvalue = self.max_v
        self.sensordegree = (self.angle_fr
                +  (self.angle_to - self.angle_fr) * (self.sensorvalue - self.min_v)
                / (self.max_v - self.min_v))

        self.x1 = self.mid * sin(radians(self.degree)) + self.x
        self.y1 = self.mid * cos(radians(self.degree)) + self.y
        self.changed = 0
        self.dot2.position(self.x1, self.y1, 0.5)
        self.dot2_alpha = 1.0
        self.set_block.set_position(
                x=(self.inner - 33) * sin(radians(self.degree - self.step)) + self.x, 
                y=(self.inner - 33) * cos(radians(self.degree - self.step)) + self.y,
                rot=-self.degree + self.step)

    def check_touch(self, touched, offset):
        updateelements = []
        self.changed = 0
        if touched:
            if ((self.x1 - 100) < peripherals.xc and peripherals.xc  < (self.x1 + 100) and
                    (self.y1 - 100) < peripherals.yc and peripherals.yc  < (self.y1 + 100)):
                self.changed = 2
                (peripherals.lastx, peripherals.lasty)  = (peripherals.xc, peripherals.yc) # reset movex, to avoid sliding while changing dial
                offset = 0
                touch_degree = int(degrees(atan2(peripherals.lastx - self.x,
                                    peripherals.lasty - self.y)))
                if self.degree != touch_degree:
                    self.degree = touch_degree
                    self.changed = 2
                    updateelements.append((self.bline, (None, 0.3, None, -1.0)))
                    peripherals.clicksound()
                    if self.degree < self.angle_fr:
                        self.degree = self.angle_fr
                    if self.degree > self.angle_to:
                        self.degree = self.angle_to
                    self.trian.rotateToZ(-self.degree+self.step)
                    self.set_block.set_position(
                            x=(self.inner - 33) * sin(radians(self.degree - self.step)) + self.x, 
                            y=(self.inner - 33) * cos(radians(self.degree - self.step)) + self.y,
                            rot=-self.degree + self.step)

                    peripherals.control(self.set_field,
                            (self.min_v + (self.degree - self.angle_fr)
                            / (self.angle_to - self.angle_fr) * (self.max_v - self.min_v)))
                    self.x1 = self.mid * sin(radians(self.degree)) + self.x
                    self.y1 = self.mid * cos(radians(self.degree)) + self.y
        else:
            set_val = getattr(peripherals.eg_object, self.set_field)
            act_val = getattr(peripherals.eg_object, self.act_field)
            if (self.value != set_val) or (self.sensorvalue != act_val) :
                self.changed = 1
                #updateelements.append((self.sensorticks, (0.2, None, None, -1.0)))

                self.value = set_val 
                self.degree = (self.angle_fr + (self.angle_to - self.angle_fr)
                        * (self.value - self.min_v) / (self.max_v - self.min_v))
                self.x1 = self.mid * sin(radians(self.degree)) + self.x
                self.y1 = self.mid * cos(radians(self.degree)) + self.y
                self.sensorvalue = act_val
                if self.dot2_alpha < 0:
                    self.val_block.set_text(text_format=self.text_format.format(self.sensorvalue))
                self.actval.regen()
                if self.sensorvalue < self.min_v:
                    self.sensorvalue = self.min_v
                if self.sensorvalue > self.max_v:
                    self.sensorvalue = self.max_v
                self.sensordegree = (self.angle_fr + (self.angle_to - self.angle_fr)
                        * (self.sensorvalue - self.min_v) / (self.max_v - self.min_v))
                updateelements.append((self.ticks, (-1.0, -1.0, 0.1, -1.0)))
                self.trian.rotateToZ(-self.degree + self.step)
                self.set_block.set_position(x= ((self.inner-33) * sin(radians(self.degree-self.step)) + self.x), 
                                   y= ((self.inner-33) * cos(radians(self.degree-self.step)) + self.y),
                                   rot=-self.degree+self.step)
                self.set_block.set_text(text_format=self.text_format.format(
                        getattr(peripherals.eg_object, self.set_field)))
                if  self.value > self.sensorvalue:
                    tick_m = (1, 0, 0)
                    z2 = None
                else:
                    tick_m = (0, 0, 1)
                    z2 = 0.4
                self.ticks.set_material(tick_m)
                updateelements.append((self.sensorticks, (0.4, None, z2, -1.0)))
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
        if self.changed > 1:
            self.val_block.set_text(text_format=self.text_format.format(
                getattr(peripherals.eg_object, self.set_field)))
            self.set_block.set_text(text_format=self.text_format.format(
                getattr(peripherals.eg_object, self.set_field)))
            rgbval = round((self.degree - self.angle_fr) / (self.angle_to - self.angle_fr), 2) # rgbval 0.0 - 1.0

            self.val_block.colouring.set_colour([rgbval, 0, 1 - rgbval])
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
                self.val_block.set_text(text_format=self.text_format.format(self.sensorvalue))
                self.val_block.colouring.set_colour([1, 1, 1])
                self.actval.regen()
                self.ticks_alpha = 0
        else:
            if self.ticks_alpha <= 1.0:
                self.ticks_alpha += 0.01
                self.ticks.set_alpha(self.ticks_alpha)
                if self.ticks_alpha >= 1.0:
                    self.ticks_alpha = 0.5
            if abs(offset) < 30:
                self.sensorticks.draw()
                self.ticks.draw()
                self.trian.draw()
        self.dial.draw()
        self.actval.draw()
