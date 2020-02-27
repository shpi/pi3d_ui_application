#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import pi3d
import time
import rrdtool

from .. import config
from ..core import  peripherals
from ..core import graphics

try:
    from _thread import start_new_thread
except:
    from thread import start_new_thread

#sys.path.insert(1, os.path.join(sys.path[0], '..'))

graph = None

def update_graph():
    global graph

    rrdtool.graph("/media/ramdisk/graph1.png", "--full-size-mode", "--font", "DEFAULT:13:", "--color", "BACK#ffffffC0", "--color", "CANVAS#ffffff00",
                  "--color", "SHADEA#ffffff00", "--color", "SHADEB#ffffff00", "--width", "800", "--height", "480",
                        #"--rigid", "--upper-limit" ,"40",
                        "--start","-2h", "--title","", "--vertical-label",'° C',
                        "DEF:act_temp=temperatures.rrd:act_temp:AVERAGE",
                        "DEF:heat=temperatures.rrd:heating:MAX",
                        "DEF:cool=temperatures.rrd:cooling:MAX",
                        "DEF:cpu=temperatures.rrd:cpu:AVERAGE",
                        "DEF:gpu=temperatures.rrd:gpu:AVERAGE",
                        "DEF:atmega=temperatures.rrd:atmega:AVERAGE",
                        "DEF:sht=temperatures.rrd:sht:AVERAGE",
                        "DEF:bmp280=temperatures.rrd:bmp280:AVERAGE",
                        "DEF:mlxamb=temperatures.rrd:mlxamb:AVERAGE",
                        "DEF:mlxobj=temperatures.rrd:mlxobj:AVERAGE",
                        "DEF:movement=temperatures.rrd:movement:MAX",
                        "CDEF:motion=movement,.5,+,FLOOR,INF,0,IF",
                        "CDEF:heating=heat,.5,+,FLOOR,1,-,UNKN,act_temp,IF",
                        "CDEF:cooling=cool,.5,+,FLOOR,1,-,UNKN,act_temp,IF",
                        #"LINE1:cpu#ff0000:CPU",
                        #"LINE1:gpu#ff0000:GPU",
                        #"LINE1:atmega#00ff00:AVR",
                        "LINE1:sht#d0d000:SHT",
                        #"LINE1:mlxamb#ff00ff:MLX_A",
                        "LINE1:mlxobj#00ffff:MLX",
                        "LINE1:bmp280#888800:BMP",
                        "AREA:act_temp#ffffcc",
                        "LINE2:act_temp#999999:Room",
                        "AREA:heating#ffcccc",
                        "LINE1:heating#ff5555:Heating",
                        "AREA:cooling#ccccff",
                        "LINE1:cooling#5555ff:Cooling",
                        "AREA:motion#00AA0070:Motion")


    graph = pi3d.ImageSprite('/media/ramdisk/graph1.png',
                             shader=graphics.SHADER, camera=graphics.CAMERA, w=800, h=480, z=1)


graphupdated = 0
update_graph()


def inloop(textchange=False, activity=False, offset=0):

    global graphupdated, graph

    if graphupdated < time.time():
        graphupdated = time.time() + 60
        start_new_thread(update_graph, ())

    if offset != 0:
        offset = graphics.slider_change(graph, offset)
    graph.draw()

    return activity, offset
