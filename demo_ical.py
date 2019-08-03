#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import random,time, os , sys
import pi3d

from random import randint

import numpy as np
import math

PIC_DIR = './backgrounds'
TMDELAY = 30  #delay for changing backgrounds
nexttm = time.time()



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

displayheight = 480

DISPLAY = pi3d.Display.create(layer=0,w=800, h= displayheight,background=(0.0, 0.0, 0.0, 1.0),frames_per_second=60, tk=False)
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



from ics import Calendar
import arrow

#c = Calendar(requests.get(url).text)


icalfile = open('muellkalender.ics', 'r')
gcal = Calendar(icalfile.readlines())



count = 0
mystring = ''
actualy = 0

for e in list(gcal.timeline.start_after(arrow.now().floor('day'))):

 if count < 5:
  size = 0.79
  titles = pi3d.TextBlock(-390, ((displayheight/2) + actualy - (pointFont.height*size*0.5)), 0.1, 0.0, 30 ,text_format= e.begin.humanize().title(), size=size, spacing="F", space=0.02, colour=(1,0,0,1))
  text.add_text_block(titles)
  
  actualy -= titles.size * pointFont.height

  size = 0.29
  date = pi3d.TextBlock(-380, ((displayheight/2) + actualy - (pointFont.height*size*0.5)), 0.1, 0.0, 12 ,text_format= '(' + e.begin.format('DD.MM.YYYY') + ')', size=size,spacing="F", space= 0.02, colour=(1,1,1,1))
  text.add_text_block(date)

  actualy -= date.size *  pointFont.height
  size = 0.4
  
  #for subtext in  textwrap.wrap(e.name, width= 20):  

  width = 0
  subtext = ''
  actualword = ''
  g_scale = float(text.point_size) / pointFont.height
  

  for c in e.name:
    width += pointFont.glyph_table[c][0] * g_scale * size
    
    actualword +=  c
    if c in (' ','-',',','.','+',':'):
     subtext += actualword 
     actualword = ''
    
    if width > 730:
     event = pi3d.TextBlock(-350, (displayheight/2) + actualy - (pointFont.height*size*0.5), 0.1, 0.0, 40, text_format = subtext, size=size,spacing="F",space =0.02,colour=(1,1,1,1))
     text.add_text_block(event)
     subtext = ''
     width = 0
     actualy -= event.size * pointFont.height
  if (subtext != '') or (actualword != ''):
   event = pi3d.TextBlock(-350, (displayheight/2) + actualy  - (pointFont.height*size*0.5), 0.1, 0.0, 40,text_format = subtext + actualword, size=size,spacing="F",space = 0.02,colour=(1,1,1,1))
   text.add_text_block(event)
   actualy -= event.size * pointFont.height




  actualy -= 20
  count+=1

 # mystring += (e.begin.humanize().title() + ' -  ' + e.begin.format('DD.MM.YYYY')  + ': ' + e.name + '\n')


 else: break



storagearea = pi3d.Sprite(camera=CAMERA,w=780,h=460,z=3, x =0, y = 0)
storagearea.set_shader(matsh)
storagearea.set_material((0.0, 0.0, 0.0))
storagearea.set_alpha(0.6)
upperboarder = pi3d.Sprite(camera=CAMERA,w=780,h=20,z=0.1, x =0, y = 240)
upperboarder.set_shader(matsh)
upperboarder.set_material((0.0, 0.0, 0.0))
upperboarder.set_alpha(0.0)
lowerboarder = pi3d.Sprite(camera=CAMERA,w=780,h=20,z=0.1, x =0, y = -240)
lowerboarder.set_shader(matsh)
lowerboarder.set_material((0.0, 0.0, 0.0))
lowerboarder.set_alpha(0.0)




slide = 1
scrolloffset = 0
updown = 0

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
     storagearea.draw()
     lowerboarder.draw()
     upperboarder.draw()
     text.draw()
     #text.regen() 
     
     if actualy < -displayheight:
      if scrolloffset <  actualy + displayheight:
         updown = 1
      if scrolloffset > 0:
         updown = 0
      if updown:    
        scrolloffset += 15
      else:
        scrolloffset -= 1
      text.text.positionY(-scrolloffset)

    
DISPLAY.destroy()
