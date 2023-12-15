
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



mydoor = pi3d.Cuboid(CAMERA3D,w=0.5,h=1,d=0.08, name="Door",x=0.25, y=0, z=0)  #child has z = 0
mydoor.set_alpha(0.9)
mydoor.set_material((0.5,0.1,0.1))
mydoor.set_draw_details(matl, [], 0.0, 1.0)

mydoorhandle = pi3d.Sphere(radius=0.03,x=0.45,z=0.05)

mydoorhandle.set_draw_details(shinesh, [], 0.0, 0.5)
mydoormerge = pi3d.MergeShape(CAMERA3D,x=0,y=0,z=2)
mydoormerge.add_child(mydoor)
mydoormerge.add_child(mydoorhandle)
angle = 180
mydoormerge.rotateToX(-20)

while DISPLAY.loop_running():



  slide.draw()
  mydoormerge.draw()

  angle += 1
  if angle > 270: angle = 180
  mydoormerge.rotateToY(angle)
  
  #mydoor.rotateIncX(0.27)
  
