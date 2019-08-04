
#!/usr/bin/python
from __future__ import absolute_import, division, print_function, unicode_literals
from math import sin, cos,radians
import pi3d
DISPLAY = pi3d.Display.create(w=800, h= 480,background=(1.0, 1.0, 1.0, 1.0), frames_per_second=60)

shaderflat = pi3d.Shader("uv_flat")
CAMERA = pi3d.Camera(is_3d=False)
CAMERA3D = pi3d.Camera(eye=(0, 0, -0.1))
slide = pi3d.ImageSprite('backgrounds/IMG-20160924-WA0008.jpg',shader=shaderflat,camera=CAMERA,w=800,h=480,z=7500)


shader = pi3d.Shader("uv_light")
shinesh = pi3d.Shader("uv_reflect")
flatsh = pi3d.Shader("uv_flat")
matsh = pi3d.Shader("mat_reflect")
matl = pi3d.Shader("mat_light")

test = pi3d.Texture('backgrounds/IMG-20160924-WA0008.jpg')



myglass = pi3d.Tube(CAMERA3D,radius=0.3,sides=30,thickness=0.05,height=1, name="Glass",x=0, y=0, z=0)  #child has z = 0
#myglass.set_alpha(0.4)
#myglass.set_material((0.1,0.1,0.1))
#myglass.set_draw_details(matl, [], 0.0, 1.0)

mybottom = pi3d.Cylinder(radius=0.3,height=0.05,sides=30,y=0,x=0,z=0)

#mybottom.set_draw_details(shinesh, [], 0.0, 0.5)


mywater = pi3d.Cylinder(radius=0.295,sides=30,height=0.7,y=0.1,x=0.1)   #y= (glassheight - waterheight / 2) - bottomheight
mywater.set_alpha(0.7)
mywater.set_material((0,0,0.7))
mywater.set_draw_details(matl,[test],0,1)
mymerge = pi3d.MergeShape(CAMERA3D,x=0,y=0,z=2)
mymerge.add(myglass,0.1)
mymerge.add(mybottom,0.1,0.475,0)

mymerge.set_alpha(0.7)
mymerge.set_material((0.1,0.1,0.1))
mymerge.set_draw_details(matl, [], 0.0, 1.0)
mymerge.add_child(mywater)
angle = 180


while DISPLAY.loop_running():



  slide.draw()
  mymerge.draw()

  angle += 1
  #if angle > 270: angle = 180
  mymerge.rotateToY(angle)
  
  mymerge.rotateIncX(0.27)
  
