#!/usr/bin/env python
# -*- coding: utf-8 -*-


from __future__ import absolute_import, division, print_function, unicode_literals
import os,time, sys

try:
 from _thread import start_new_thread
except:
 from thread import start_new_thread

try:
    unichr
except NameError:
    unichr = chr



import numpy as np
import rrdtool
import pi3d
import importlib

from io import BytesIO
from PIL import Image

import core.graphics as graphics
import core.peripherals as peripherals

import config
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

slides = []
subslides = dict()

for  slidestring in config.slides:
      slides.append(importlib.import_module('slides.'+slidestring))

for  slidestring in config.subslides: 
      subslides[slidestring] = importlib.import_module('subslides.'+slidestring)



a = 0
screenshot = None


def get_files():
  
  file_list = []
  extensions = ['.png','.jpg','.jpeg']
  for root, dirnames, filenames in os.walk(config.installpath + 'backgrounds'):
    for filename in filenames:
      ext = os.path.splitext(filename)[1].lower()
      if ext in extensions and not filename.startswith('.'):
        file_list.append(os.path.join(root, filename))
  #random.shuffle(file_list)

  return file_list, len(file_list)



if config.startmqttclient:
  import core.mqttclient as mqttclient
  try: mqttclient.init()
  except: pass

if config.starthttpserver:
  try:
   from http.server import BaseHTTPRequestHandler, HTTPServer              #ThreadingHTTPServer for python 3.7
  except:
   from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

  from core.httpserver import ServerHandler

  try:
   littleserver = HTTPServer(("0.0.0.0", config.HTTP_PORT), ServerHandler)
    #littleserver = ThreadingHTTPServer(("0.0.0.0", 9000), ServerHandler)
   littleserver.timeout = 0.1
  except:
    print('server error')



slide_offset = 0 # change by touch and slide
textchange = True
sfg, sbg = None, None
now = time.time()

def sensor_thread():
 global textchange,a,sbg,sfg,now
 last_backlight_level = 0
 iFiles, nFi = get_files()
 pic_num = nFi - 1
 sfg = graphics.tex_load(iFiles[pic_num])
 nextsensorcheck = 0
 everysecond = 0
 nexttm = 0
 
 while True:

   if now > nexttm:                                     # change background
      nexttm = now + config.TMDELAY
      
      sbg = sfg
      sbg.positionZ(5)
      pic_num = (pic_num + 1) % nFi
      sfg = graphics.tex_load(iFiles[pic_num])
      a = 0

   if peripherals.eg_object.alert:
      peripherals.alert()
   elif config.subslide == 'alert': #alert == 0
      peripherals.alert(0)
      config.subslide = None
      if config.startmqttclient:   mqttclient.publish('alert','off')

   if config.backlight_auto:

    if now < peripherals.eg_object.lastmotion + config.backlight_auto:
      peripherals.eg_object.backlight_level = peripherals.eg_object.max_backlight 

    else:
      peripherals.eg_object.backlight_level = 0


   if peripherals.eg_object.backlight_level != last_backlight_level:
      print('set backlight:' + str(peripherals.eg_object.backlight_level))
      peripherals.controlbacklight(peripherals.eg_object.backlight_level)
      last_backlight_level = peripherals.eg_object.backlight_level


   if config.starthttpserver:
          littleserver.handle_request()
   else:
      time.sleep(0.1)

   if config.startmqttclient: mqttclient.publishall()
   


   if (now > everysecond):
     peripherals.get_infrared()
     everysecond = now + config.INFRARED_TM

   if (now > nextsensorcheck):

    peripherals.get_sensors() 
    nextsensorcheck = now + config.SENSOR_TM

    if config.coolingrelay and config.coolingrelay == config.heatingrelay:
        peripherals.coolingheating()
    else:    
      if config.coolingrelay: peripherals.cooling()
      if config.heatingrelay: peripherals.heating()

    peripherals.get_status()   
    textchange = True
    if hasattr(peripherals.eg_object,'bmp280_temp'): bmp280_temp = peripherals.eg_object.bmp280_temp
    else: bmp280_temp = 0

    if hasattr(peripherals.eg_object,'sht_temp'): sht_temp = peripherals.eg_object.sht_temp
    else: sht_temp = 0

    temperatures_str = 'N:{:.2f}:{:.2f}:{:.2f}:{:.2f}:{:.2f}:{:.2f}:{:.2f}:{:.2f}:{:.2f}'.format(
      peripherals.eg_object.act_temp, peripherals.eg_object.gputemp, peripherals.eg_object.cputemp, peripherals.eg_object.atmega_temp,
      sht_temp, bmp280_temp, peripherals.eg_object.mlxamb, peripherals.eg_object.mlxobj,(0.0))
    print(temperatures_str)
    rrdtool.update(str('temperatures.rrd'), str(temperatures_str))
    

    if config.show_airquality:
        redvalue = 255 if peripherals.eg_object.a4 > 600 else int(0.03 * peripherals.eg_object.a4)
        greenvalue = 0 if peripherals.eg_object.a4 > 400 else int(0.02*(400 - peripherals.eg_object.a4))
        peripherals.controlled([redvalue,greenvalue,0])




autoslide = time.time() + config.autoslidetm

peripherals.eg_object.slide = config.slide

start_new_thread(sensor_thread,())


time.sleep(1)

while graphics.DISPLAY.loop_running():

  now = time.time()



  if not config.subslide:

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
      
      if (abs(movex) > 40):                              #calculate slider movement
        slide_offset = movex

  else:
    #autoslide demo mode
    if len(config.autoslides) and peripherals.eg_object.backlight_level > 0  and peripherals.lasttouch + 10 < now  and  now > autoslide:
     movex +=10
     slide_offset = movex
     if movex > 300: autoslide = time.time() + config.autoslidetm
    else:
     movex = 0
     peripherals.lastx = 0

  if movex < -300 and peripherals.eg_object.slide > 0 and peripherals.lasttouch < (now - 0.1):     #start sliding when there is enough touchmovement
    peripherals.lastx = 0
    movex = 0
    peripherals.eg_object.slide -= 1
    sbg.set_alpha(0)
    if config.slideshadow: a = 0
    slide_offset += 400
    

  if movex > 300  and peripherals.lasttouch < (now - 0.1):
    peripherals.lastx = 0
    movex = 0
    if peripherals.eg_object.slide < len(config.slides) -1 :
       peripherals.eg_object.slide += 1

    else: peripherals.eg_object.slide = 0

    if (not peripherals.touched() and len(config.autoslideints)): 
         config.autoslideints = np.roll(config.autoslideints,1)
         peripherals.eg_object.slide = config.autoslideints[0]
         
    else:
      sbg.set_alpha(0)
      if config.slideshadow: a = 0
    slide_offset -= 400

  if config.subslide != None: 
   activity = subslides[config.subslide].inloop(textchange,activity)
  
  elif -1 < peripherals.eg_object.slide < len(config.slides):
   
   activity,slide_offset = slides[peripherals.eg_object.slide].inloop(textchange,activity,slide_offset)  
  
  if (textchange): textchange = False
  if (activity == False) & (slide_offset == 0) :  time.sleep(0.1)
  activity = False

  while (peripherals.eg_object.backlight_level == 0): 
           time.sleep(0.1)
           now = time.time()

  if (os.path.exists("/media/ramdisk/screenshot.png") == False):
               print('make screenshot')
               pi3d.screenshot("/media/ramdisk/screenshot.png")




graphics.DISPLAY.destroy()
