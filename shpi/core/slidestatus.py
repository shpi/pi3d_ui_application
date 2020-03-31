#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from pkg_resources import resource_filename

import pi3d

from .. import config
from ..core import peripherals
from ..core import graphics


class SlideStatus(object):

  def __init__(self, x=0, y=-235, radius=4, camera=graphics.CAMERA,shader=graphics.MATSH):

      self.x = x - ((10*len(config.slides)) / 2) + radius
      self.status = []
      

      self.md = pi3d.MergeShape(name="merged dots",camera=graphics.CAMERA)

      disk = pi3d.Disk(radius=radius, sides=7, z=0.2, rx=90,x=x,y=y, camera=camera)

      for x1 in range(len(config.slides)):

          self.md.add(disk.buf[0], x=self.x + (10*x1), y=y, z=0.2, rx=90) 
 

      self.md.set_shader(graphics.MATSH)
      self.md.set_material((1.0, 1.0, 1.0))
      self.md.set_alpha(0.5)



      self.actslide = pi3d.Disk(radius=radius,sides=7,z=0.1,x=self.x+(10*config.slide),rx=90,y=y, camera=camera)
      self.actslide.set_shader(shader)
      self.actslide.set_material((1,1,1))
      self.actslide.set_alpha(1)



  def update(self,actslide):

      self.actslide.positionX(self.x+(10*actslide))


  def draw(self):

      self.md.draw()
      self.actslide.draw()


