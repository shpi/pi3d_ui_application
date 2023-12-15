#!/usr/bin/python
from __future__ import absolute_import, division, print_function, unicode_literals
''' Uses the pi3d.Graph class added to pi3d develop branch on Friday 13th Oct 2017
'''

import pi3d,smbus
import numpy as np


bus = smbus.SMBus(2)  
LINES = True # change this to see bar graph

display = pi3d.Display.create(w=800, h=480, background=(0,0,0,1), frames_per_second=30)
font = pi3d.Font("opensans.ttf")
key = pi3d.Keyboard()


if LINES:
  x_vals = np.linspace(0, 500, 500)
  y_vals = np.zeros((2, 500))

W, H = 800, 480
xpos = (display.width - W) / 2
ypos = (display.height - H) / 2

graph = pi3d.Graph(x_vals, y_vals, W, H, font, title='Infrared Temperature Demo',
              line_width=3, xpos=xpos, ypos=ypos,
              axes_desc=['o', 'celsius'], legend = ['internal', 'object'],
              ymax=40,ymin=20)

while display.loop_running():
  graph.draw()
  try:
   mlxamb = ((bus.read_word_data(0x5b, 0x26) *0.02)  - 273.15)
   mlxobj = ((bus.read_word_data(0x5b, 0x27) *0.02)  - 273.15)
  except:
   pass
  y_vals[0] = np.roll(y_vals[0], -1)
  y_vals[1] = np.roll(y_vals[1], -1)
  y_vals[0][499] = mlxamb
  y_vals[1][499] = mlxobj 
  graph.update(y_vals)

