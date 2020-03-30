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
      x2 = 0
      for x1 in range(len(config.slides)):
        
        self.status.append(pi3d.Disk(radius=radius, sides=7, z=0.2, rx=90,x=self.x+(10*x1),y=y, camera=camera))
        self.status[x2].set_shader(shader)
        self.status[x2].set_material((1, 1, 1))
        self.status[x2].set_alpha(0.1)
        x2 += 1
        self.status.append(pi3d.Disk(radius=radius+1, sides=7, z=0.3, rx=90,x=self.x+(10*x1),y=y, camera=camera))
        self.status[x2].set_shader(shader)
        self.status[x2].set_material((0, 0, 0))
        self.status[x2].set_alpha(0.8)
        x2 += 1


      self.actslide = pi3d.Disk(radius=radius,sides=7,z=0.1,x=self.x+(10*config.slide),rx=90,y=y, camera=camera)
      self.actslide.set_shader(shader)
      self.actslide.set_material((1,1,1))
      self.actslide.set_alpha(1)



  def update(self,actslide):

      self.actslide.positionX(self.x+(10*actslide))


  def draw(self):

      for dot in self.status:
          dot.draw()

      self.actslide.draw()


