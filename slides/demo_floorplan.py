#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pi3d
import sys,os

sys.path.insert(1, os.path.join(sys.path[0], '..'))

import config
import core.graphics as graphics
import core.peripherals as peripherals



text = pi3d.PointText(graphics.pointFont, graphics.CAMERA, max_chars=35, point_size=256) 

temp_block = pi3d.TextBlock(-200, -100, 0.1, 0.0, 15, data_obj=peripherals.eg_object, attr="act_temp",text_format= chr(0xE021) +" {:2.1f}°C", size=0.2, spacing="F", space=0.02, colour=(1.0, 1.0, 1.0, 1.0))
text.add_text_block(temp_block)


officearea = pi3d.Sprite(camera=graphics.CAMERA,w=380,h=220,z=3, x = -70, y = 110)
officearea.set_shader(graphics.MATSH)
officearea.set_material((1.0, 0.0, 0.0))

kitchenarea = pi3d.Sprite(camera=graphics.CAMERA,w=220,h=200,z=3, x = -140, y = -110)
kitchenarea.set_shader(graphics.MATSH)
kitchenarea.set_material((0.0, 1.0, 0.0))

storagearea = pi3d.Sprite(camera=graphics.CAMERA,w=140,h=220,z=3, x = 190, y = 110)
storagearea.set_shader(graphics.MATSH)
storagearea.set_material((0.0, 0.0, 1.0))



floorplan = pi3d.ImageSprite('sprites/floorplan.png',shader=graphics.SHADER, camera=graphics.CAMERA,w=539, h=450, x=0, y=0, z=2.0)
doorneedle = pi3d.Lines(camera=graphics.CAMERA, vertices=((0,0,0),(60,0,0)), material=(1.0, 0.3, 0.0), line_width=20, x=-13.0, y=-220.0, z=1.0)
doorneedle.set_shader(graphics.MATSH)

windowneedle = pi3d.Lines(camera=graphics.CAMERA, vertices=((0,0,0),(45,0,0)), material=(0, 1, 0.0), line_width=10, x=-180.0, y=217.0, z=1.0)
windowneedle.set_shader(graphics.MATSH)
rotate = 0

      
        
        
def inloop(textchange = False,activity = False, offset = 0):
     global rotate
 
     if textchange:
       text.regen()


     rotate = rotate+1
     if rotate > 90: rotate = 0
     doorneedle.rotateToZ(rotate)  #open  rotate 0 closed
     doorneedle.set_material([rotate*1.1*0.01,0,0])
     windowneedle.set_material([rotate*1.1*0.01,100-rotate*1.1*0.01,0])
     windowneedle.rotateToZ(-rotate)
      

     if offset == 0: 
      officearea.draw()
      kitchenarea.draw()
      storagearea.draw()
      doorneedle.draw()
      windowneedle.draw()

     floorplan.draw()
     
     officearea.set_alpha(0.01 * rotate)
     kitchenarea.set_alpha(1 - 0.01 * rotate)
     storagearea.set_alpha(0.01*rotate) 
        
        
     if offset != 0:
         offset = graphics.slider_change(floorplan, offset)
         if offset == 0:
             text.regen()

     text.draw()   
     activity = True    
     return activity,offset




















