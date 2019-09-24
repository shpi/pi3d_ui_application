#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys,os,time
import pi3d


sys.path.insert(1, os.path.join(sys.path[0], '..'))

import subslides.wifisetup as wifisetup
import config
import core.graphics as graphics
import core.peripherals as peripherals
              
chars = []
chars.append(pi3d.PointText(graphics.pointFont, graphics.CAMERA, max_chars=220, point_size=128))   
chars.append(pi3d.PointText(graphics.pointFont, graphics.CAMERA, max_chars=220, point_size=128))    
chars.append(pi3d.PointText(graphics.pointFont, graphics.CAMERA, max_chars=220, point_size=128))    
keyboardslide = pi3d.PointText(graphics.pointFont, graphics.CAMERA, max_chars=220, point_size=128)    

wifistatus = pi3d.PointText(graphics.pointFont, graphics.CAMERA, max_chars=320, point_size=128)    

charmap = []

charmap.append(['01234567','89!#$%^;','/*()-_+=', "~`[]{}|\\","\"'<>,.?"+chr(0xE03F)])
charmap.append(['abcdefgh','ijklmnop','qrstuvwx', 'yzäöüß@_' ,chr(0xE036)+'      '+chr(0xE03F)])
charmap.append(['ABCDEFGH','IJKLMNOP','QRSTUVWX', 'YZÄÖÜ°&_' ,chr(0xE036)+'      '+chr(0xE03F)])

def calculatechar(type, x, y):
  global charmap

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
bbox.set_shader(graphics.MATSH)

textfield = pi3d.Sprite(camera=graphics.CAMERA,w=590,h=70,z=3, x = -95, y =195)
textfield.set_shader(graphics.MATSH)
textfield.set_material((0.0, 0.0, 0.0))
textfield.set_alpha(0.7)

controlok= pi3d.FixedString(config.installpath + 'fonts/opensans.ttf', (str)(chr(0xE03E)), font_size=65,shadow_radius=4, 
                        background_color=(0,0,0,0), color= (255,255,255,255),
                        camera=graphics.CAMERA, shader=graphics.SHADER, f_type='SMOOTH')
controlok.sprite.position(245, 196, 1)


controlx= pi3d.FixedString(config.installpath + 'fonts/opensans.ttf', (str)(chr(0xE01E)), font_size=65,shadow_radius=4, 
                        background_color=(0,0,0,0), color= (255,255,255,255),
                        camera=graphics.CAMERA, shader=graphics.SHADER, f_type='SMOOTH')
controlx.sprite.position(335, 196, 1)

keyboardfield = pi3d.Sprite(camera=graphics.CAMERA,w=780,h = 380,z=3, x = 0, y =-40)
keyboardfield.set_shader(graphics.MATSH)
keyboardfield.set_material((0.0, 0.0, 0.0))
keyboardfield.set_alpha(0.7)


textblock = pi3d.TextBlock(-370, 195, 0.1, 0.0, 27, data_obj=peripherals.eg_object,attr="usertextshow",text_format= "{:s}", size=0.29, spacing="F", space=0.05, colour=(1.0, 1.0, 1.0, 1.0))
keyboardslide.add_text_block(textblock)


chartype = 0
everysecond = 0

        
def inloop(x = 0, y = 0, touch_pressed = False, textchange = False,activity = False):

     global chartype,everysecond
     if peripherals.touch_pressed:
      peripherals.touch_pressed = False
      if 150 < peripherals.lasty <  240:
       if 192 < peripherals.lastx < 289:
        config.subslide = None
        #print(wifinetworks[calculateselectednetwork]['essid'])
        #print(eg_object.usertext)
        file = open('/etc/wpa_supplicant/wpa_supplicant.conf','w') 
        file.write('country=US\n') 
        file.write('ctrl_interface=/var/run/wpa_supplicant GROUP=netdev\n') 
        file.write('update_config=1\n') 
        file.write('network={\n') 
        file.write('ssid="' + wifisetup.wifinetworks[wifisetup.selectednetwork]['essid'] + '"\n') 
        if wifisetup.wifinetworks[wifisetup.selectednetwork]['essid'] == 'hidden':
           file.write('scan_ssid=1\n')

        if wifisetup.wifinetworks[wifisetup.selectednetwork]['enc'] == 'off':
          file.write('key_mgmt=NONE\n')
        elif wifisetup.wifinetworks[wifisetup.selectednetwork]['enc'] == 'WPA2': 
          file.write('psk="' + peripherals.eg_object.usertext  +  '"\n') 
        elif wifisetup.wifinetworks[wifisetup.selectednetwork]['enc'] == 'on': 
          file.write('wep_tx_keyidx=0\n')
          file.write('wep_key0="'+ peripherals.eg_object.usertext  +'"\n')
          file.write('key_mgmt=NONE\n')
        elif wifisetup.wifinetworks[wifisetup.selectednetwork]['enc'] == 'WPA' :
          file.write('psk="' + peripherals.eg_object.usertext  +  '"\n') 
          file.write('pairwise=CCMP\n')
          file.write('group=TKIP\n')

        file.write('}') 
        file.close() 
        #os.popen('sudo wpa_cli -i wlan0 reconfigure')
        os.popen('sudo ifdown wlan0')
        os.popen('sudo ifup wlan0')


        #sudo systemctl daemon-reload
        #sudo systemctl restart dhcpcd
        #sudo systemctl reenable wpa_supplicant.service
        #sudo systemctl restart wpa_supplicant.service
        #sudo systemctl restart dhcpcd.service
        #sudo wpa_supplicant -B -Dwext -i wlan0 -c /etc/wpa_supplicant/wpa_supplicant.conf
       elif peripherals.lastx > 289:
         config.subslide= None
         wifisetup.wifinetworks = None


      else: 
       newchar  =   calculatechar(chartype,peripherals.lastx,peripherals.lasty)
       
       if newchar == chr(0xE036):
           peripherals.eg_object.usertext = peripherals.eg_object.usertext[:-1]
           
       elif newchar == chr(0xE03F): 
         chartype += 1
         if chartype > 2: chartype = 0
       else: 
        peripherals.eg_object.usertext +=  (str)(newchar)
       
       peripherals.eg_object.usertextshow = peripherals.eg_object.usertext[-24:]

       if peripherals.eg_object.usertext == '':
        peripherals.eg_object.usertextshow = '|' 
       activity = True
       keyboardslide.regen()
      
     if everysecond < time.time():
      if peripherals.eg_object.usertext != '':
       if  (int)(everysecond)%2==0:
        peripherals.eg_object.usertextshow = peripherals.eg_object.usertext[-24:] + '|'
       else: 
        peripherals.eg_object.usertextshow = peripherals.eg_object.usertext[-24:]  
      activity = True
      keyboardslide.regen()
      everysecond = time.time() + 1

     textfield.draw()
     keyboardslide.draw()
     keyboardfield.draw()
     controlok.draw()     
     controlx.draw()
     chars[chartype].draw()
     bbox.draw()




         
     return activity




















