#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import random,time, os , sys
import pi3d
import MinGraph
from random import randint

import numpy as np
import math

PIC_DIR = './backgrounds'
TMDELAY = 30  #delay for changing backgrounds
nexttm = time.time()


class EgClass(object):
  mlxobj = 0.0
  mlxamb = 0.0
  sht_temp = 0.0

eg_object = EgClass()





#get all background files
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



# chars and symbols for GUI

mytext = '()\nß1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZüöäÜÖÄ,.%:° -'
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


DISPLAY = pi3d.Display.create(samples = 4, layer=0,w=800, h=480,background=(0.0, 0.0, 0.0, 1.0),frames_per_second=60, tk=False)
shader = pi3d.Shader("uv_flat")
CAMERA = pi3d.Camera(is_3d=False)

def tex_load(fname):
  slide = pi3d.ImageSprite(fname,shader=shader,camera=CAMERA,w=800,h=480,z=4)
  slide.set_alpha(0)
  return slide

sfg = tex_load(iFiles[pic_num])

pointFont = pi3d.Font("opensans.ttf", shadow=(0, 0, 0, 255), shadow_radius=5, grid_size=11,
                       codepoints=mytext, add_codepoints=additional)

text = pi3d.PointText(pointFont, CAMERA, max_chars=1000, point_size=128)    #slide 1

matsh = pi3d.Shader("mat_flat")


x_vals = np.linspace(0, 780, 780)
y_vals = np.zeros((3,780))

colors = [(1,0,0,1),(0,0.5,0,1),(0,0,1,1)]

graph = MinGraph.MinGraph(x_vals, y_vals, 780, 460, 
              line_width=2,camera=CAMERA,shader=matsh,colorarray=colors, xpos=0, ypos=0 , z = 1.0, ymax=40,ymin=0)


legend1 = pi3d.TextBlock(-340, 150, 0.1, 0.0, 15, data_obj=eg_object,text_format= "MLX O:  {:2.1f}", attr="mlxobj",size=0.5, spacing="C", space=1.1, colour=colors[0])
text.add_text_block(legend1)

legend2 = pi3d.TextBlock(-340, 100, 0.1, 0.0, 15, data_obj=eg_object,text_format= "MLX A:  {:2.1f}", attr="mlxamb",size=0.5, spacing="C", space=1.1, colour=colors[1])
text.add_text_block(legend2)

legend2 = pi3d.TextBlock(-340, 50, 0.1, 0.0, 15, data_obj=eg_object,text_format=  "SHT:    {:2.1f}", attr="sht_temp",size=0.5, spacing="C", space=1.1, colour=colors[2])
text.add_text_block(legend2)





grapharea = pi3d.Sprite(camera=CAMERA,w=780,h=460,z=3, x =0, y = 0)
grapharea.set_shader(matsh)
grapharea.set_material((1.0, 1.0, 1.0))
grapharea.set_alpha(0.6)

slide = 1
mlxobj = 0
mlxamb = 0
sht_temp= 0

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
     grapharea.draw()
     text.draw()
     text.regen()
     graph.draw()
     
     y_vals[0][:-1] = y_vals[0][1:]
     y_vals[1][:-1] = y_vals[1][1:]
     y_vals[2][:-1] = y_vals[2][1:]
     try:
      bus.write_i2c_block_data(0x44, 0x2C, [0x06])
      eg_object.mlxamb = ((bus.read_word_data(0x5b, 0x26) *0.02)  - 273.15)
      eg_object.mlxobj = ((bus.read_word_data(0x5b, 0x27) *0.02)  - 273.15)
     
      time.sleep(0.01)
      data = bus.read_i2c_block_data(0x44, 0x00, 6)
      eg_object.sht_temp = float(((((data[0] * 256.0) + data[1]) * 175) / 65535.0) - 45)
     except:

      eg_object.mlxobj += 0.3
      eg_object.mlxamb -= 0.4
      eg_object.sht_temp += 0.5
      if eg_object.sht_temp > 40: eg_object.sht_temp = 4
      if eg_object.mlxamb < 20:  eg_object.mlxamb = 34
      if eg_object.mlxobj > 40: eg_object.mlxobj = 1
      pass  
     
     y_vals[0][-1] = eg_object.mlxobj
     y_vals[1][-1] = eg_object.mlxamb
     y_vals[2][-1] = eg_object.sht_temp
 
     graph.update(y_vals)


  time.sleep(0.02)

DISPLAY.destroy()
