#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from math import sin, cos, radians
from pkg_resources import resource_filename

import pi3d

from .. import config
from ..core import peripherals
from ..core import graphics


class WifiStatus(object):

  def __init__(self, step=3, x=370, y=210, camera=graphics.CAMERA,shader=graphics.MATSH):

      shape = [[],[],[]]
      self.wifi_lines = []

      for x1 in range(-45, 45, step):
          s, c = sin(radians(x1)), cos(radians(x1))
          shape[0].append((7 * s, 7 * c, 0.1))
          shape[1].append((14 * s, 14 * c, 0.1))
          shape[2].append((21 * s, 21 * c, 0.1))


      self.wifi_lines.append(pi3d.Disk(radius=2, sides=7, z=0.1, rx=90,x=x,y=y, camera=camera))
      self.wifi_lines[0].set_shader(shader)
      self.wifi_lines[0].set_material((1, 1, 1))

      for x1 in range(3):
          self.wifi_lines.append(pi3d.Lines(vertices=shape[x1], line_width=3,x=x,y=y, strip=True))
          self.wifi_lines[x1+1].set_shader(shader)
          self.wifi_lines[x1+1].set_material((1, 1, 1))

  def update(self):

      try:
          wifistrength = int((os.popen("/sbin/iwconfig wlan0 | grep 'Signal level' | awk '{print $4}' | cut -d= -f2 | cut -d/ -f1;").readline()).strip())
          assert -100 < wifistrength <= 0, "value outside permitted range"

      except:
          wifistrength = -100

      DBMTOPERCENT = [-100,-83,-70,-53]

      for dbm in range(0,4):

        if int(wifistrength) > DBMTOPERCENT[dbm]:
            self.wifi_lines[dbm].set_alpha(1)
        else:
            self.wifi_lines[dbm].set_alpha(0.3)

  def draw(self):

      for line in self.wifi_lines:
          line.draw()



#wifistatus = WifiStatus()
#wifistatus.update()
#wifistatus.draw()


