#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals
import os, subprocess,random ,time, sys
from random import randint
import math
import struct
import datetime

import rrdtool
import pi3d
import importlib


import core.peripherals as peripherals
import config
import core.graphics as graphics

slides = []
subslides = dict()

for  slidestring in config.slides:
 slides.append(importlib.import_module('slides.'+slidestring))

for  slidestring in config.subslides: 
 subslides[slidestring] = importlib.import_module('subslides.'+slidestring)





# make 4M ramdisk for graph
os.popen('sudo mkdir /media/ramdisk')
os.popen('sudo mount -t tmpfs -o size=4M tmpfs /media/ramdisk')
#os.chdir('/media/ramdisk')


if not os.path.isfile('temperatures.rrd'):
    print('create rrd')
    rrdtool.create(
    "temperatures.rrd",
    "--step","60",
    "DS:act_temp:GAUGE:120:-127:127",
    "DS:gpu:GAUGE:120:-127:127",
    "DS:cpu:GAUGE:120:-127:127",
    "DS:atmega:GAUGE:120:-127:127",
    "DS:sht:GAUGE:120:-127:127",
    "DS:bmp280:GAUGE:120:-127:127",
    "DS:mlxamb:GAUGE:120:-127:127",
    "DS:mlxobj:GAUGE:120:-127:127",
    "DS:ntc:GAUGE:120:-127:127",
    "RRA:MAX:0.5:1:1500",
    "RRA:MAX:0.5:10:1500",
    "RRA:MAX:0.5:60:1500")



nextsensorcheck = 0
everysecond = 0
nexttm = 0
last_backlight_level = 0 



def get_files():
  
  file_list = []
  extensions = ['.png','.jpg','.jpeg']
  for root, dirnames, filenames in os.walk(config.installpath + 'backgrounds'):
    for filename in filenames:
      ext = os.path.splitext(filename)[1].lower()
      if ext in extensions and not filename.startswith('.'):
        file_list.append(os.path.join(root, filename))
  random.shuffle(file_list)

  return file_list, len(file_list)

iFiles, nFi = get_files()
pic_num = nFi - 1



if config.starthttpserver:
  from http.server import BaseHTTPRequestHandler, HTTPServer              #ThreadingHTTPServer for python 3.7
  from core.httpserver import ServerHandler

  try:
    littleserver = HTTPServer(("0.0.0.0", 9000), ServerHandler)
    #littleserver = ThreadingHTTPServer(("0.0.0.0", 9000), ServerHandler)
    littleserver.timeout = 0.1
  except:
    print('server error')




slide_offset = 0 # change by touch and slide
textchange = True
sfg = graphics.tex_load(iFiles[pic_num])


while graphics.DISPLAY.loop_running():

  now = time.time()

  if config.backlight_auto:

    next_tm = peripherals.eg_object.lastmotion + config.backlight_auto
    if peripherals.eg_object.backlight_level and next_tm  < now:
      peripherals.eg_object.backlight_level = int(peripherals.eg_object.max_backlight - (now - next_tm)) 

    elif peripherals.eg_object.backlight_level < peripherals.eg_object.max_backlight and next_tm > now:
      peripherals.eg_object.backlight_level = peripherals.eg_object.max_backlight


    if peripherals.eg_object.backlight_level != last_backlight_level:
      peripherals.controlbacklight(peripherals.eg_object.backlight_level)
      last_backlight_level = peripherals.eg_object.backlight_level



  if (now > everysecond):
    peripherals.get_infrared()
    everysecond = now + config.INFRARED_TM


  if (now > nextsensorcheck):

    if config.coolingrelay and config.coolingrelay == config.heatingrelay:
        peripherals.coolingheating()
    else:    
      if config.coolingrelay: peripherals.cooling()
      if config.heatingrelay: peripherals.heating()


    peripherals.get_sensors()
    nextsensorcheck = now + config.SENSOR_TM


    if config.show_airquality:
        redvalue = int(0.03 * peripherals.eg_object.a4)
    if (peripherals.eg_object.a4 > 400):
          greenvalue = 0
    else:
          greenvalue = int(0.02*(400 - peripherals.eg_object.a4))
    peripherals.controlled([redvalue,greenvalue,0])


    textchange = True



  if not config.subslide:

    if now > nexttm and not peripherals.touched():                                     # change background
      nexttm = now + config.TMDELAY
      a = 0.0
      sbg = sfg
      sbg.positionZ(4)
      pic_num = (pic_num + 1) % nFi
      sfg = graphics.tex_load(iFiles[pic_num])

    if a < 1.0:                                              # fade to new background
      activity = True  #we calculate   more frames, when there is activity, otherwise we add sleep.time at end
      a += 0.01
      sbg.draw()
      sfg.set_alpha(a)

    sfg.draw()


  if peripherals.touched(): # and (peripherals.lasttouch + 0.4 > time.time()):  # check if touch is pressed, to detect sliding
    x,y = peripherals.get_touch()
    activity = True
    if ((x != 400) and peripherals.lastx):  #catch 0,0 -> 400,-240
      movex = (peripherals.lastx - x)
      movey = (peripherals.lasty - x)
      if (abs(movex) > 50):                              #calculate slider movement
        slide_offset = movex

  else:
    movex = 0

  if movex < -300 and config.slide > 0:     #start sliding when there is enough touchmovement
    peripherals.lastx = 0
    movex = 0
    config.slide = config.slide - 1
    sbg.set_alpha(0)
    a = 0
    slide_offset += 400


  if movex > 300 and config.slide < len(config.slides) - 1:
    peripherals.lastx = 0
    movex = 0
    config.slide = config.slide + 1
    sbg.set_alpha(0)
    a = 0
    slide_offset -= 400


  if config.subslide != None: 
   subslides[config.subslide].inloop(textchange,activity)

  elif -1 < config.slide < len(config.slides):
   activity,slide_offset = slides[config.slide].inloop(peripherals.lastx,peripherals.lasty,peripherals.touch_pressed,textchange,activity,slide_offset)
  


  if (activity == False) & (slide_offset == 0) : 
      if config.starthttpserver:
          littleserver.handle_request()
      #else:
      #    time.sleep(0.1)
  activity = False
  textchange = False
  



graphics.DISPLAY.destroy()
