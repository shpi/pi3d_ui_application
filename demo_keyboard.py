#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import random,time, os , sys
import pi3d
import RPi.GPIO as gpio
from random import randint

import numpy as np
import math, smbus

PIC_DIR = './backgrounds'
TMDELAY = 30  #delay for changing backgrounds
nexttm = time.time()
TOUCHINT = 26
TOUCHADDR = 0x5C
xc = 0
yc = 0

bus = smbus.SMBus(2)
gpio.setmode(gpio.BCM)
gpio.setwarnings(False)
gpio.setup(TOUCHINT, gpio.IN)




class EgClass(object):
  usertext = (str)('')
  usertextshow = '|' 
eg_object = EgClass()



try:
 bus.write_byte_data(TOUCHADDR,0x6e,0b00001110)                                              # interrupt confi$
 bus.write_byte_data(TOUCHADDR,0x70,0b00000000)
except:
 print('no touchscreen found')
 TOUCHADDR = False
 pass


def get_touch():
  global  xc,yc
  if TOUCHADDR:     
   try:
         data = bus.read_i2c_block_data(TOUCHADDR, 0x40, 8)
         x1 = 400 - (data[0] | (data[4] << 8))
         y1 = (data[1] | (data[5] << 8)) - 240

         if ((-401 < x1  < 401) & (-241 < y1  < 241)):
          if ((-80 < (xc-x1) < 80) & (-80 < (yc-y1) < 80)):  #catch bounches 
           xc = x1
           yc = y1
           #print(x1,y1)
           return x1,y1  #compensate position to match with PI3D
          else:
           xc = x1
           yc = y1

           print('not identical')
           return get_touch()
         else: 
          return get_touch()


   except:
       time.sleep(0.06)  #wait on  I2C error
       print('i2cerror')
       return get_touch() 
       pass    

  else:
    return 0,0       

lastx = 0
lasty = 0
touch_pressed = False
lasttouch = 0

def touch_debounce(channel):  
 global lastx, lasty, touch_pressed,lasttouch
 x,y = get_touch()
 lasttouch = time.time()
 if (channel == TOUCHINT):
 # if ADDR_32U4:
 #  bus.write_byte_data(ADDR_32U4, 0x92, 0x01) #click sound
  touch_pressed = True  
  lastx = x
  lasty = y
 else:
  return x,y;


gpio.add_event_detect(TOUCHINT, gpio.RISING, callback=touch_debounce, bouncetime=100)    #touch interrupt



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

mytext = '°abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()-_+=~`[]{}|\:;"\'<>,.?/ üöäÜÖÄß'
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
              chr(0xE03F), #chars
              #chr(0xE00D), #cloudsun
              #chr(0xE00E), #lightoff
              chr(0xE00F), #lighton
              chr(0xE010), #settings
              #chr(0xE011), #heart
              chr(0xE012), #book
              chr(0xE036), #delete
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
              chr(0xE03E), #ok
              chr(0xE02F)] #cam


DISPLAY = pi3d.Display.create(layer=0,w=800, h=480,background=(0.0, 0.0, 0.0, 1.0),frames_per_second=60, tk=False)
shader = pi3d.Shader("uv_flat")
CAMERA = pi3d.Camera(is_3d=False)

def tex_load(fname):
  slide = pi3d.ImageSprite(fname,shader=shader,camera=CAMERA,w=800,h=480,z=4)
  slide.set_alpha(0)
  return slide

sfg = tex_load(iFiles[pic_num])

pointFont = pi3d.Font("opensans.ttf", shadow=(0, 0, 0, 255), shadow_radius=5, grid_size=12,
                       codepoints=mytext, add_codepoints=additional)
chars = []
chars.append(pi3d.PointText(pointFont, CAMERA, max_chars=220, point_size=128))    #slide 1
chars.append(pi3d.PointText(pointFont, CAMERA, max_chars=220, point_size=128))    #slide 1
chars.append(pi3d.PointText(pointFont, CAMERA, max_chars=220, point_size=128))    #slide 1
keyboardslide = pi3d.PointText(pointFont, CAMERA, max_chars=220, point_size=128)    #slide 1


matsh = pi3d.Shader("mat_flat")



charmap = []

charmap.append(['01234567','89!#$%^;','/*()-_+=', "~`[]{}|\\","\"'<>,.?"+chr(0xE03F)])
charmap.append(['abcdefgh','ijklmnop','qrstuvwx', 'yzäöüß@_' ,chr(0xE036)+'      '+chr(0xE03F)])
charmap.append(['ABCDEFGH','IJKLMNOP','QRSTUVWX', 'YZÄÖÜ°&_' ,chr(0xE036)+'      '+chr(0xE03F)])

def calculatechar(type, x, y):
  global charmap
  #print(type)
  #print(x)
  #print(y)
  i = -1
  e = -1
  if -390 < x <  -293:
   i = 0
  elif -293 < x < -196:
   i = 1
  elif -196 < x < -99:
   i = 2
  elif -99 < x < -2:
   i = 3
  elif -2 < x < 95:
   i = 4
  elif 95 < x < 192:
   i = 5
  elif 192 < x < 289:
   i = 6
  elif 289 < x < 390:
   i = 7

  if -230 < y  < -154:
   e = 4
  elif -154 < y < -78:
   e = 3
  elif -78 < y < -2:
   e = 2
  elif -2 <  y < 74:
   e = 1
  elif  74 < y < 150:
   e = 0
  
  if e > -1 and i > -1:
     return charmap[type][e][i]
  else: return (str)('')


numberblock = pi3d.TextBlock(-345, 110, 0.1, 0.0, 8,text_format=  charmap[0][0], size=0.69, spacing="C", space=2.2, colour=(1.0, 1.0, 1.0, 1.0))
chars[0].add_text_block(numberblock)
numberblock = pi3d.TextBlock(-345, 35, 0.1, 0.0, 8,text_format= charmap[0][1], size=0.69, spacing="C", space=2.2, colour=(1.0, 1.0, 1.0, 1.0))
chars[0].add_text_block(numberblock)
numberblock = pi3d.TextBlock(-345, -40, 0.1, 0.0, 8,text_format= charmap[0][2], size=0.69, spacing="C", space=2.2, colour=(1.0, 1.0, 1.0, 1.0))
chars[0].add_text_block(numberblock)
numberblock = pi3d.TextBlock(-345, -115, 0.1, 0.0, 8,text_format= charmap[0][3], size=0.69, spacing="C", space=2.2, colour=(1.0, 1.0, 1.0, 1.0))
chars[0].add_text_block(numberblock)
numberblock = pi3d.TextBlock(-345, -190, 0.1, 0.0, 8,text_format= charmap[0][4], size=0.69, spacing="C", space=2.2, colour=(1.0, 1.0, 1.0, 1.0))
chars[0].add_text_block(numberblock)
letterblock = pi3d.TextBlock(-345, 110, 0.1, 0.0, 8,text_format= charmap[1][0], size=0.69, spacing="C", space=2.2, colour=(1.0, 1.0, 1.0, 1.0))
chars[1].add_text_block(letterblock)
letterblock = pi3d.TextBlock(-345, 35, 0.1, 0.0, 8,text_format= charmap[1][1], size=0.69, spacing="C", space=2.2, colour=(1.0, 1.0, 1.0, 1.0))
chars[1].add_text_block(letterblock)
letterblock = pi3d.TextBlock(-345, -40, 0.1, 0.0, 8,text_format= charmap[1][2], size=0.69, spacing="C", space=2.2, colour=(1.0, 1.0, 1.0, 1.0))
chars[1].add_text_block(letterblock)
letterblock = pi3d.TextBlock(-345, -115, 0.1, 0.0, 9,text_format= charmap[1][3], size=0.69, spacing="C", space=2.2, colour=(1.0, 1.0, 1.0, 1.0))
chars[1].add_text_block(letterblock)
letterblock = pi3d.TextBlock(-345, -190, 0.1, 0.0, 9,text_format= charmap[1][4], size=0.69, spacing="C", space=2.2, colour=(1.0, 1.0, 1.0, 1.0))
chars[1].add_text_block(letterblock)

letterblock = pi3d.TextBlock(-345, 110, 0.1, 0.0, 8,text_format= charmap[2][0], size=0.69, spacing="C", space=2.2, colour=(1.0, 1.0, 1.0, 1.0))
chars[2].add_text_block(letterblock)
letterblock = pi3d.TextBlock(-345, 35, 0.1, 0.0, 8,text_format= charmap[2][1], size=0.69, spacing="C", space=2.2, colour=(1.0, 1.0, 1.0, 1.0))
chars[2].add_text_block(letterblock)
letterblock = pi3d.TextBlock(-345, -40, 0.1, 0.0, 8,text_format= charmap[2][2], size=0.69, spacing="C", space=2.2, colour=(1.0, 1.0, 1.0, 1.0))
chars[2].add_text_block(letterblock)
letterblock = pi3d.TextBlock(-345, -115, 0.1, 0.0, 9,text_format= charmap[2][3], size=0.69, spacing="C", space=2.2, colour=(1.0, 1.0, 1.0, 1.0))
chars[2].add_text_block(letterblock)
letterblock = pi3d.TextBlock(-345, -190, 0.1, 0.0, 9,text_format= charmap[2][4], size=0.69, spacing="C", space=2.2, colour=(1.0, 1.0, 1.0, 1.0))
chars[2].add_text_block(letterblock)



Z = 1.0
bbox_vertices = [[-390,  150, Z],
                 [ 390,  150, Z],
                 [ 390, -230, Z],
                 [-390, -230, Z],
                 [-390,  150, Z],
                 [-293,  150, Z],
                 [-293, -230, Z], 
                 [-196, -230, Z],
                 [-196,  150, Z],
                 [ -99,  150, Z],
                 [ -99, -230, Z],
                 [  -2, -230, Z],
                 [  -2,  150, Z],
                 [ 95,  150 ,Z],
                 [ 95, -230, Z],
                 [ 192, -230, Z],
                 [ 192,  150, Z],
                 [ 289,  150, Z],
                 [ 289, -230, Z],
                 [ 390, -230, Z],
                 [ 390, -154, Z],
                 [-390, -154, Z],
                 [-390, -78, Z],
                 [ 390, -78, Z],
                 [ 390, -2, Z],
                 [-390, -2, Z],
                 [-390, 74, Z],
                 [390, 74, Z],
				]

bbox = pi3d.Lines(vertices=bbox_vertices, material=(1.0,0.8,0.05), closed=False, line_width=4) 
bbox.set_alpha(0.1)
bbox.set_shader(matsh)

textfield = pi3d.Sprite(camera=CAMERA,w=500,h=70,z=3, x = -140, y =195)
textfield.set_shader(matsh)
textfield.set_material((0.0, 0.0, 0.0))
textfield.set_alpha(0.7)


keyboardfield = pi3d.Sprite(camera=CAMERA,w=780,h = 380,z=3, x = 0, y =-40)
keyboardfield.set_shader(matsh)
keyboardfield.set_material((0.0, 0.0, 0.0))
keyboardfield.set_alpha(0.7)


textblock = pi3d.TextBlock(-370, 195, 0.1, 0.0, 25, data_obj=eg_object,attr="usertextshow",text_format= "{:s}", size=0.29, spacing="F", space=0.05, colour=(1.0, 1.0, 1.0, 1.0))

keyboardslide.add_text_block(textblock)


everysecond = time.time()

chartype = 0

slide = 1
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
     if touch_pressed:
       touch_pressed = False
       newchar  =   calculatechar(chartype,lastx,lasty)
       print(newchar)
       if newchar == chr(0xE036):
           eg_object.usertext = eg_object.usertext[:-1]
       elif newchar == chr(0xE03F): 
         chartype += 1
         if chartype > 2: chartype = 0
       else: 
        eg_object.usertext +=  (str)(newchar)
       if eg_object.usertext != '': 
         eg_object.usertextshow = eg_object.usertext[-24:]
         keyboardslide.regen()
      
     if everysecond < time.time():
      
      if  (int)(everysecond)%2==0 or eg_object.usertext == (str)(''):
       eg_object.usertextshow = eg_object.usertext[-24:] + '|'
      else: eg_object.usertextshow = eg_object.usertext[-24:]  
      keyboardslide.regen()
      everysecond = time.time() + 1

     textfield.draw()
     keyboardslide.draw()
     keyboardfield.draw()
     
     chars[chartype].draw()
     bbox.draw()

  time.sleep(0.0)

DISPLAY.destroy()
