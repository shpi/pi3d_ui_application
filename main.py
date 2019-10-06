#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals
import os,time, sys
from _thread import start_new_thread

import rrdtool
import pi3d
import importlib

import core.graphics as graphics
import core.peripherals as peripherals
import config




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
a = 0






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

iFiles, nFi = get_files()
pic_num = nFi - 1

if config.startmqttclient:
  import core.mqttclient as mqttclient
  try: mqttclient.init()
  except: pass

if config.starthttpserver:
  from http.server import BaseHTTPRequestHandler, HTTPServer              #ThreadingHTTPServer for python 3.7
  from core.httpserver import ServerHandler

  try:
    littleserver = HTTPServer(("0.0.0.0", config.HTTP_PORT), ServerHandler)
    #littleserver = ThreadingHTTPServer(("0.0.0.0", 9000), ServerHandler)
    littleserver.timeout = 0.1
  except:
    print('server error')




slide_offset = 0 # change by touch and slide
textchange = True
sfg = graphics.tex_load(iFiles[pic_num])

print(os.popen('i2cdetect -y 2').readlines())

peripherals.get_infrared() #run all one for init eg_object
peripherals.get_sensors() # ''
peripherals.get_status() # ''

peripherals.eg_object.slide = config.slide

while graphics.DISPLAY.loop_running():

  now = time.time()

  if peripherals.eg_object.alert:
    peripherals.alert()
  elif config.subslide == 'alert':
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


    start_new_thread(peripherals.get_status,())

    
    if hasattr(peripherals.eg_object,'bmp280_temp'): bmp280_temp = peripherals.eg_object.bmp280_temp
    else: bmp280_temp = 0

    if hasattr(peripherals.eg_object,'sht_temp'): sht_temp = peripherals.eg_object.sht_temp
    else: sht_temp = 0



    
    temperatures_str = 'N:{:.2f}:{:.2f}:{:.2f}:{:.2f}:{:.2f}:{:.2f}:{:.2f}:{:.2f}:{:.2f}'.format(
      peripherals.eg_object.act_temp, peripherals.eg_object.gputemp, peripherals.eg_object.cputemp, peripherals.eg_object.atmega_temp,
      sht_temp, bmp280_temp, peripherals.eg_object.mlxamb, peripherals.eg_object.mlxobj,(0.0))

    start_new_thread(rrdtool.update,('temperatures.rrd', temperatures_str))
    #rrdtool.update('temperatures.rrd', temperatures_str)
    print(temperatures_str)


    if config.show_airquality:
        redvalue = int(0.03 * peripherals.eg_object.a4)
        greenvalue = 0 if peripherals.eg_object.a4 > 400 else int(0.02*(400 - peripherals.eg_object.a4))
        peripherals.controlled([redvalue,greenvalue,0])

    if config.startmqttclient: mqttclient.publishall()
    
    textchange = True



  if not config.subslide:

    if now > nexttm and not peripherals.touched():                                     # change background
      nexttm = now + config.TMDELAY
      a = 0.0
      sbg = sfg
      sbg.positionZ(5)
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
      #movey = (peripherals.lasty - y)
      if (abs(movex) > 50):                              #calculate slider movement
        slide_offset = movex

  else:
    movex = 0

  if movex < -300 and peripherals.eg_object.slide > 0:     #start sliding when there is enough touchmovement
    peripherals.lastx = 0
    movex = 0
    peripherals.eg_object.slide -= 1
    sbg.set_alpha(0)
    a = 0
    slide_offset += 400


  if movex > 300 and peripherals.eg_object.slide < len(config.slides) - 1:
    peripherals.lastx = 0
    movex = 0
    peripherals.eg_object.slide += 1
    sbg.set_alpha(0)
    a = 0
    slide_offset -= 400


  if config.subslide != None: 
   activity = subslides[config.subslide].inloop(textchange,activity)

  elif -1 < peripherals.eg_object.slide < len(config.slides):
   #print(peripherals.eg_object.slide)
   activity,slide_offset = slides[peripherals.eg_object.slide].inloop(textchange,activity,slide_offset)  


  if (activity == False) & (slide_offset == 0) : 
      if config.starthttpserver:
          littleserver.handle_request()
      #else:
      #    time.sleep(0.1)
  activity = False
  textchange = False
  



graphics.DISPLAY.destroy()
