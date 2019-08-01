#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import random,time, os , sys
import pi3d

import subprocess
from random import randint

import numpy as np
import math
import struct

PIC_DIR = './backgrounds'
TMDELAY = 30  #delay for changing backgrounds
nexttm = time.time()


def get_files():
  global PIC_DIR
  file_list = []
  extensions = ['.png','.jpg','.jpeg']
  for root, dirnames, filenames in os.walk(PIC_DIR):
    for filename in filenames:
      ext = os.path.splitext(filename)[1].lower()
      if ext in extensions and not filename.startswith('.'):
        file_list.append(os.path.join(root, filename))
  random.shuffle(file_list)

  return file_list, len(file_list)

iFiles, nFi = get_files()
pic_num = nFi - 1


class EgClass(object):
  set_temp = 23.0
  atmega_volt = 0
  backlight_level = 0
  mlxamb = 0.0
  mlxobj = 0.0
  bmp280_temp = 0.0
  sht_temp = 0.0
  gputemp =  0
  cputemp =  0
  atmega_temp = 0
  act_temp = 23.0
  useddisk = "0%"
  load = 0.0
  freespace = 0.0
  wifistrength = " "
  ipaddress = " "
  led_red = 0
  led_green = 0
  led_blue = 0
  vent_rpm = 0
  vent_pwm = 0
  ssid = " "
  uhrzeit = "00:00"
  atmega_ram = 0
  humidity = 0.0
  pressure = 0.0
  relais1 = 0
  relais2 = 0
  relais3 = 0
  d13 = 0
  hwb = 0
  a0 = 0
  a2 = 0
  a3 = 0
  a4 = 0
  a5 = 0
  a7 = 0
  lightlevel = 0
  buzzer = 0
  a1 = 0
  lastmotion = time.time()
  relais1current = 0.0

eg_object = EgClass()


# chars and symbols for GUI

mytext = '1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZüöäÜÖÄ,.%:° -'
additional = [chr(0xE000), #arrow
              chr(0xE001), #circle
              chr(0xE002), #cloud
              chr(0xE003), #raindrop
              chr(0xE004), #fire
              chr(0xE005), #house
              #chr(0xE006), #filledcircle
              #chr(0xE007), #raining
              #chr(0xE008), #timer
              chr(0xE009), #clock
              #chr(0xE00A), #eye
              chr(0xE00B), #gauge
              chr(0xE00C), #sun
              #chr(0xE00D), #cloudsun
              #chr(0xE00E), #lightoff
              chr(0xE00F), #lighton
              chr(0xE010), #settings
              #chr(0xE011), #heart
              #chr(0xE012), #book
              #chr(0xE013), #child
              #chr(0xE014), #alarmclock
              #chr(0xE015), #presence
              #chr(0xE016), #wifi
              #chr(0xE017), #mic
              #chr(0xE018), #bluetooth
              #chr(0xE019), #web
              #chr(0xE01A), #speechbubble
              #chr(0xE01B), #ampere
              chr(0xE01C), #motion
              #chr(0xE01D), #electric
              #chr(0xE01E), #close
              #chr(0xE01F), #leaf
              #chr(0xE020), #socket
              chr(0xE021), #temp
              #chr(0xE022), #tesla
              #chr(0xE023), #raspi
              #chr(0xE024), #privacy
              #chr(0xE025), #circle2
              #chr(0xE026), #bell
              #chr(0xE027), #nobell
              #chr(0xE028), #moon
              chr(0xE029), #freeze
              #chr(0xE02A), #whatsapp
              #chr(0xE02B), #touch
              #chr(0xE02C), #settings2
              #chr(0xE02D), #storm
              chr(0xE035), #shutter
              #chr(0xE034), #doublearrow
              #chr(0xE033), #usb
              #chr(0xE032), #magnet
              chr(0xE031), #phone
              #chr(0xE030), #compass
              #chr(0xE02E), #trash
              chr(0xE02F)] #cam


DISPLAY = pi3d.Display.create(layer=0,w=800, h=480,background=(0.0, 0.0, 0.0, 1.0),frames_per_second=60, tk=False)
shader = pi3d.Shader("uv_flat")
CAMERA = pi3d.Camera(is_3d=False)

def tex_load(fname):
  slide = pi3d.ImageSprite(fname,shader=shader,camera=CAMERA,w=800,h=480,z=4)
  slide.set_alpha(0)
  return slide

sfg = tex_load(iFiles[pic_num])

pointFont = pi3d.Font("opensans.ttf", shadow=(0, 0, 0, 255), shadow_radius=5, grid_size=11,
                       codepoints=mytext, add_codepoints=additional)

text = pi3d.PointText(pointFont, CAMERA, max_chars=220, point_size=128)    #slide 1

matsh = pi3d.Shader("mat_flat")


#slider1

temp_block = pi3d.TextBlock(-60, 50, 0.1, 0.0, 15, data_obj=eg_object,attr="act_temp",text_format= chr(0xE021) +"{:2.1f}°C", size=0.39, spacing="F", space=0.02, colour=(1.0, 1.0, 1.0, 1.0))
text.add_text_block(temp_block)

temp_block2 = pi3d.TextBlock(-200, -100, 0.1, 0.0, 15, data_obj=eg_object,attr="act_temp",text_format= chr(0xE021) +"{:2.1f}°C", size=0.39, spacing="F", space=0.02, colour=(1.0, 1.0, 1.0, 1.0))
text.add_text_block(temp_block2)
officearea = pi3d.Sprite(camera=CAMERA,w=380,h=220,z=2, x = -70, y = 110)
officearea.set_shader(matsh)
officearea.set_material((1.0, 0.0, 0.0))
officearea.set_alpha(0.3)


kitchenarea = pi3d.Sprite(camera=CAMERA,w=220,h=200,z=2, x = -140, y = -110)
kitchenarea.set_shader(matsh)
kitchenarea.set_material((0.0, 1.0, 0.0))
kitchenarea.set_alpha(0.3)


storagearea = pi3d.Sprite(camera=CAMERA,w=140,h=220,z=2, x = 190, y = 110)
storagearea.set_shader(matsh)
storagearea.set_material((0.0, 0.0, 1.0))
storagearea.set_alpha(0.3)



slide = 1
floorplan = pi3d.ImageSprite('floorplan.png',shader=shader, camera=CAMERA,w=539, h=450, x=0, y=0, z=3.0)
doorneedle = pi3d.Lines(camera=CAMERA, vertices=((0,0,0),(60,0,0)), material=(1.0, 0.3, 0.0), line_width=10, x=-13.0, y=-220.0, z=1.0)
doorneedle.set_shader(matsh)

windowneedle = pi3d.Lines(camera=CAMERA, vertices=((0,0,0),(45,0,0)), material=(0, 1, 0.0), line_width=10, x=-180.0, y=217.0, z=1.0)
windowneedle.set_shader(matsh)
rotate = 0

while DISPLAY.loop_running():
  
     

  if slide > 0:

    if time.time() > nexttm:                                     # change background
      nexttm = time.time() + TMDELAY
      a = 0.0
      sbg = sfg
      sbg.positionZ(5)
      pic_num = (pic_num + 1) % nFi
      sfg = tex_load(iFiles[pic_num])

    if a < 1.0:                                              # fade to new background
      activity = True  #we calculate   more frames, when there is activity, otherwise we add sleep.time at end
      a += 0.01
      sbg.draw()
      sfg.set_alpha(a)

    sfg.draw()
    
    
  if slide == 1:
     rotate = rotate+1
     if rotate > 90: rotate = 0
     doorneedle.rotateToZ(rotate)  #open  rotate 0 closed
     doorneedle.set_material([rotate*1.1*0.01,0,0])
     windowneedle.set_material([rotate*1.1*0.01,100-rotate*1.1*0.01,0])
     windowneedle.rotateToZ(-rotate)
     doorneedle.draw()
     windowneedle.draw()
     floorplan.draw()
     text.draw()
     text.regen() 
     officearea.set_alpha(0.005 * rotate)
     kitchenarea.set_alpha(0.6-0.01 * rotate)
     officearea.draw() 
     kitchenarea.draw() 
     storagearea.draw()  

  time.sleep(0.1)

DISPLAY.destroy()
