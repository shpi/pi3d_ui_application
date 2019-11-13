#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys,os

try:
 from _thread import start_new_thread
except:
 from thread import start_new_thread

import pi3d
import time
import rrdtool


sys.path.insert(1, os.path.join(sys.path[0], '..'))


import config
import core.graphics as graphics
import core.peripherals as peripherals
graph = None
def update_graph():
      global graph
      rrdtool.graph("/media/ramdisk/graph1.png" ,"--full-size-mode","--font","DEFAULT:13:","--color","BACK#ffffffC0","--color","CANVAS#ffffff00",
      "--color","SHADEA#ffffff00","--color","SHADEB#ffffff00","--width","800","--height","480","--start","-1h","--title","temperature overview","--vertical-label","°C",
      "DEF:act_temp=temperatures.rrd:act_temp:AVERAGE",
      "DEF:cpu=temperatures.rrd:cpu:AVERAGE",
      "DEF:gpu=temperatures.rrd:gpu:AVERAGE",
      "DEF:atmega=temperatures.rrd:atmega:AVERAGE",
      "DEF:sht=temperatures.rrd:sht:AVERAGE",
      "DEF:bmp280=temperatures.rrd:bmp280:AVERAGE",
      "DEF:mlxamb=temperatures.rrd:mlxamb:AVERAGE",
      "DEF:mlxobj=temperatures.rrd:mlxobj:AVERAGE",
      "LINE4:act_temp#ff0000:ROOM",
      "LINE2:cpu#ff0000:CPU",
      "LINE2:gpu#ff0000:GPU",
      "LINE2:atmega#00ff00:AVR",
      "LINE2:sht#0000ff:SHT30",
      "LINE2:mlxamb#ff00ff:MLX_A",
      "LINE2:mlxobj#00ffff:MLX_O",
      "LINE2:bmp280#888800:BMP280")
      graph = pi3d.ImageSprite('/media/ramdisk/graph1.png',shader=graphics.SHADER,camera=graphics.CAMERA,w=800,h=480,z=1)
 

graphupdated = 0
update_graph()
 
def inloop(textchange = False,activity = False, offset = 0):

    global graphupdated,graph 

    if graphupdated < time.time():
      graphupdated = time.time() + 60
      start_new_thread(update_graph,())


    if offset != 0:
      offset = graphics.slider_change(graph, offset)
    graph.draw()

    return activity,offset
