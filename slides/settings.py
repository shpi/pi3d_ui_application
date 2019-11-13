#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys,os

import pi3d

sys.path.insert(1, os.path.join(sys.path[0], '..'))

import config
import core.graphics as graphics
import core.peripherals as peripherals


try:
    unichr
except NameError:
    unichr = chr



text2 = pi3d.PointText(graphics.pointFont, graphics.CAMERA, max_chars=500, point_size=128) 



title_block = pi3d.TextBlock(-200, 190, 0.1, 0.0, 15, text_format= "Backlight", size=0.79, spacing="F", space=0.05, colour=(1.0, 1.0, 1.0, 1.0))
text2.add_text_block(title_block)
bllevel = pi3d.TextBlock(-50, 100, 0.1, 0.0, 15, data_obj=peripherals.eg_object,attr="max_backlight", text_format= "{:d}", size=0.99, spacing="F", space=0.05, colour=(1.0, 1.0, 1.0, 1.0))
text2.add_text_block(bllevel)
Down = pi3d.TextBlock(200, 100, 0.1, 0.0, 1, text_format= unichr(0xE000),size=0.69, spacing="C", space=0.6, colour=(1, 1, 1, 0.8))
text2.add_text_block(Down)
Up = pi3d.TextBlock(-200, 100, 0.1, 180.0, 1, text_format= unichr(0xE000),size=0.69, spacing="C", space=0.6, colour=(1, 1, 1, 0.8))
text2.add_text_block(Up)
  
newtxt = pi3d.TextBlock(-400, -180, 0.1, 0.0, 15, text_format = unichr(0xE001), size=0.99, spacing="F", space=0.05, colour = (1.0, 1.0, 1.0, 1.0))
text2.add_text_block(newtxt)
wifi = pi3d.TextBlock(-365, -170, 0.1, 0.0, 15, text_format = unichr(0xE016), size=0.79, spacing="F", space=0.05, colour = (1.0, 1.0, 1.0, 1.0))
text2.add_text_block(wifi)       



textblock = pi3d.TextBlock(-270, 0, 0.1, 0.0, 170, data_obj=peripherals.eg_object,attr="ssid",text_format= "SSID: {:s}", size=0.29, spacing="F", space=0.05, colour=(1.0, 1.0, 1.0, 1.0))
text2.add_text_block(textblock)

textblock = pi3d.TextBlock(-270, -50, 0.1, 0.0, 27, data_obj=peripherals.eg_object,attr="wifistrength",text_format= "Signal: {:s}dBm", size=0.29, spacing="F", space=0.05, colour=(1.0, 1.0, 1.0, 1.0))
text2.add_text_block(textblock)

textblock = pi3d.TextBlock(-270, -100, 0.1, 0.0, 47, data_obj=peripherals.eg_object,attr="ipaddress",text_format= "IP: {:s}", size=0.29, spacing="F", space=0.05, colour=(1.0, 1.0, 1.0, 1.0))
text2.add_text_block(textblock)








def inloop(textchange = False,activity = False, offset = 0):
         
     
     if textchange:
       text2.regen()
 

     if peripherals.touch_pressed:
      peripherals.touch_pressed = False
      if peripherals.clicked(Up.x,Up.y):
        peripherals.eg_object.max_backlight += 1
        if peripherals.eg_object.max_backlight > 31:
          peripherals.eg_object.max_backlight = 31
        peripherals.controlbacklight(peripherals.eg_object.max_backlight)
        text2.regen()


      elif peripherals.clicked(Down.x,Down.y):
        peripherals.eg_object.max_backlight -= 1
        if peripherals.eg_object.max_backlight < 1:
          peripherals.eg_object.max_backlight = 1        
        peripherals.controlbacklight(peripherals.eg_object.max_backlight)
        text2.regen()
        
      elif peripherals.clicked(wifi.x,wifi.y):
         config.subslide = 'wifisetup'
         
        
     if offset != 0:
         offset = graphics.slider_change(text2.text, offset)
         if offset == 0:
             text2.regen()
     text2.draw()   
         
     return activity,offset




















