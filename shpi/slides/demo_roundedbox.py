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

try:
    unichr
except NameError:
    unichr = chr



class RoundCorner(Shape):
  """ 3d model inherits from Shape"""
  def __init__(self, camera=None, light=None, radius=1, sides=12, name="", x=0.0, y=0.0, z=0.0,
               rx=0.0, ry=0.0, rz=0.0, sx=1.0, sy=1.0, sz=1.0,
               cx=0.0, cy=0.0, cz=0.0):
    """uses standard constructor for Shape extra Keyword arguments:

      *radius*
        Radius of disk.
      *sides*
        Number of sides to polygon representing disk.
    """
    super(RoundCorner, self).__init__(camera, light, name, x, y, z, rx, ry, rz, sx, sy, sz,
                               cx, cy, cz)


    verts = []
    norms = []
    inds = []
    texcoords = []
    self.sides = sides

    st = (pi/2) / sides 
    for j in range(-1, 1):
      verts.append((0.0, -0.1*j, 0.0))
      norms.append((0.0, -j, 0.0))
      texcoords.append((0.5, 0.5))
      for r in range(0,sides+1):
        ca, sa = Utility.from_polar_rad(r * st)
        verts.append((radius * sa, 0.0, radius * ca))
        norms.append((0.0, -j - 0.1*j, 0.0))
        texcoords.append((sa * 0.5 + 0.5, ca * 0.5 + 0.5))
      if j == -1:
        v0, v1, v2 = 0, 1, 2
      else:
        v0, v1, v2 = sides + 2, sides + 4, sides + 3 # i.e. reverse direction to show on back
      for r in range(sides):
        inds.append((v0, r + v1, r + v2))

    self.buf = [Buffer(self, verts, texcoords, inds, norms)]



class Box(object):
    def __init__(self, width = 500, height=300, radius= 30, x = 0 , y = 0, z = 0.1, alpha = 0.5):

       

        self.dot1= RoundCorner(radius=radius, sides=5, camera=graphics.CAMERA)
        self.rect = pi3d.Sprite(camera=graphics.CAMERA, w=width-(radius*2), h=height)
        self.rect2 = pi3d.Sprite(camera=graphics.CAMERA, w=width, h=height-(radius*2))

        self.mrb = pi3d.MergeShape(name="merged rounded box",camera=graphics.CAMERA)
        self.mrb.set_shader(graphics.MATSH)
        self.mrb.add(self.dot1.buf[0], x-width/2+radius,y-height/2+radius,z,rz=270, rx=90) #bot left
        self.mrb.add(self.dot1.buf[0], x+width/2-radius,y+height/2-radius,z,rz=90, rx=90)  #top right
        self.mrb.add(self.dot1.buf[0], x-width/2+radius,y+height/2-radius,z,rz=180, rx=90) #top left
        self.mrb.add(self.dot1.buf[0], x+width/2-radius,y-height/2+radius,z,rz=0, rx=90)   #bot right
        self.mrb.add(self.rect.buf[0], x,y,z) 
        self.mrb.add(self.rect2.buf[0], x,y,z)

        self.mrb.set_material((1.0, 1.0, 1.0))
        self.mrb.set_alpha(alpha)

    def draw(self):

       self.mrb.draw()
       

box = Box()


def inloop(textchange=False, activity=False, offset=0):

    #if peripherals.touched():
    box.draw()

    if offset != 0:
        offset = graphics.slider_change(box.mrb, offset)

        if offset == 0:
            textchange = True

    #if textchange:



    return activity, offset
