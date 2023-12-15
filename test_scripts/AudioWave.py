#!/usr/bin/python
from __future__ import absolute_import, division, print_function, unicode_literals
''' Uses the pi3d.Graph class added to pi3d develop branch on Friday 13th Oct 2017
'''

import pi3d,smbus
import numpy as np
import pyaudio
import time


LINES = True # change this to see bar graph
display = pi3d.Display.create(w=800, h=480, background=(0,0,0,1), frames_per_second=60)
font = pi3d.Font("opensans.ttf")


CHUNK = int(44100/60)
if LINES:
  x_vals = np.linspace(0, CHUNK, CHUNK)
  y_vals = np.zeros((2,CHUNK))  

W, H = 800, 480
xpos = (display.width - W) / 2
ypos = (display.height - H) / 2

graph = pi3d.Graph(x_vals, y_vals, W, H, font, title='Audio Demo',
              line_width=3, xpos=xpos, ypos=ypos,
              axes_desc=['TIME', 'Audio'], legend = [' ', ' '],
              ymax=15000,ymin=-15000)



p=pyaudio.PyAudio()

CHUNK = int(44100/60)

stream=p.open(format=pyaudio.paInt16,channels=1,rate=44100,
              input=True, input_device_index = 0, frames_per_buffer=CHUNK)


while display.loop_running():
  graph.draw()  
  data = np.fromstring(stream.read(CHUNK,exception_on_overflow = False),dtype=np.int16)
  y_vals[0] = data
  graph.update(y_vals)
   
