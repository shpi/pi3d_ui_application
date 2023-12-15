#!/usr/bin/python
from __future__ import absolute_import, division, print_function, unicode_literals
''' Uses the pi3d.Graph class added to pi3d develop branch on Friday 13th Oct 2017
'''

import pi3d,smbus
import numpy as np
import time

bus = smbus.SMBus(2)  
LINES = True # change this to see bar graph

display = pi3d.Display.create(w=800, h=480, background=(0,0,0,1), frames_per_second=60)
font = pi3d.Font("opensans.ttf")



if LINES:
  x_vals = np.linspace(0, 200, 200)
  y_vals = np.zeros((2, 200))

W, H = 800, 480
xpos = (display.width - W) / 2
ypos = (display.height - H) / 2

graph = pi3d.Graph(x_vals, y_vals, W, H, font, title='Air Quality Demo',
              line_width=3, xpos=xpos, ypos=ypos,
              axes_desc=['TIME', 'A4 - MP135'], legend = [' ', ' '],
              ymax=800,ymin=0)

while display.loop_running():
  graph.draw()
  y_vals[0] = np.roll(y_vals[0], -1)
  #y_vals[1] = np.roll(y_vals[1], -1)
  bus.write_byte(0x2a, 0x04)
  #time.sleep(0.01)
  lowb = bus.read_byte(0x2a)
  highb = bus.read_byte(0x2a)
  #print('\n\r')
  #print(lowb)
  #print(highb)
  #print(format((lowb | highb <<8),'#d') + ' '  + format((lowb & 0xFF) | (highb << 8),'016b'))
  
  mlxamb = ((lowb & 0xFF) | (highb << 8))
  y_vals[0][199] = mlxamb
  #y_vals[1][499] = mlxamb
 
  graph.update(y_vals)
  
