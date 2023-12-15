#!/usr/bin/python
from __future__ import absolute_import, division, print_function, unicode_literals
from math import sin, cos,radians
import pi3d
DISPLAY = pi3d.Display.create(w=800, h= 480,background=(1.0, 1.0, 1.0, 1.0), frames_per_second=60)

shaderflat = pi3d.Shader("uv_flat")
CAMERA = pi3d.Camera(is_3d=False)
CAMERA3D = pi3d.Camera()
slide = pi3d.ImageSprite('backgrounds/IMG-20160924-WA0008.jpg',shader=shaderflat,camera=CAMERA,w=800,h=480,z=7500)


shader = pi3d.Shader("uv_light")
shinesh = pi3d.Shader("uv_reflect")
flatsh = pi3d.Shader("uv_flat")
matsh = pi3d.Shader("mat_reflect")
matl = pi3d.Shader("mat_light")

test = pi3d.Texture('backgrounds/IMG-20160924-WA0008.jpg')

shape = []
shape.append((0,0))

for x in range(0,270):
 shape.append((sin(radians(x)), cos(radians(x))))
shape.append((0,0))


shape2 = []
shape2.append((0,0))

for x in range(270,361):
 shape2.append((sin(radians(x)), cos(radians(x))))
shape2.append((0,0))


myextrude = pi3d.Extrude(CAMERA3D,path=shape, height=0.4, name="Extrude",x=0, y=0, z=3)
myextrude.set_alpha(0.7)
myextrude.set_material((1, 0.6, 0.0))
myextrude.set_draw_details(matl, [], 0.0, 1.0)

myextrude2 = pi3d.Extrude(CAMERA3D,path=shape2, height=0.5, name="Extrude2",x=-0.1, y=0, z=0.1)
myextrude2.set_alpha(0.8)
myextrude2.set_material((0,0,1))
myextrude2.set_draw_details(shinesh, [test], 0.0, 1.0)

myextrude.add_child(myextrude2)

#merged = pi3d.MergeShape(CAMERA3D,x=1,y=1, z=3)
#merged.add(myextrude)
#merged.set_material((1.0, 0, 0))
#merged.add(myextrude2)
#merged.set_draw_details(matl, [], 0.0, 1.0)


while DISPLAY.loop_running():



  slide.draw()
  myextrude.draw()
  #merged.draw()  
  #merged.rotateIncY(-1)
  #merged.rotateIncX(0.10)

  myextrude.rotateIncY(-1)
  myextrude.rotateIncX(0.27)
  
