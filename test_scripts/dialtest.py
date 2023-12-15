from __future__ import absolute_import, division, print_function, unicode_literals
from math import sin, cos, radians, atan2, degrees
import pi3d
import RPi.GPIO as gpio
import i2c
import time


class Dial(object):
    def __init__(self, angle_fr=-135, angle_to=135, step=5, outer=240, inner=200,
                min_t=15, max_t=35, shader=None, camera=None):

        self.angle_fr = angle_fr
        self.angle_to = angle_to
        self.step = step
        self.outer = outer
        self.inner = inner
        self.mid = (outer + inner) / 2
        self.min_t = min_t
        self.max_t = max_t

        gpio.setmode(gpio.BCM)
        gpio.setwarnings(False)
        gpio.setup(26, gpio.IN, pull_up_down=gpio.PUD_DOWN)

        self.bus = i2c.I2C(2)

        try:
            self.bus.read(1, 0x5c)
            self.bus.write([0x6e, 0b00001110], 0x5c)
            self.bus.write([0x70, 0b00000000], 0x5c)
        except:
            print('Error: no touchscreen found')

        tick_verts = []
        dial_verts = []
        # first make tick vertices
        for x in range(self.angle_fr, self.angle_to, self.step):
            (s, c) = (sin(radians(x)), cos(radians(x))) # re-use for brevity below
            tick_verts.extend([(self.inner * s, self.inner * c, 0.1),
                                (self.outer * s, self.outer * c, 0.1)])
            dial_verts.append((self.mid * s, self.mid * c, 2.0))

        if shader is None:
            shader = pi3d.Shader('mat_flat')
        if camera is None:
            camera = pi3d.Camera(is_3d=False)
        uv_shader = pi3d.Shader('uv_flat')

        tex = pi3d.Texture('color_gradient.jpg')

        self.ticks = pi3d.PolygonLines(camera=camera, vertices=tick_verts, strip=False, line_width=5)
        
        self.ticks.set_shader(shader)
        self.ticks.set_alpha(0.8)

        self.sensorticks = pi3d.PolygonLines(camera=camera, vertices=tick_verts, line_width=5, strip=False)
        self.sensorticks.set_shader(shader)

        self.bline = pi3d.PolygonLines(camera=camera, vertices=dial_verts, line_width=40)
        self.bline.set_textures([tex])
        self.bline.set_alpha(0.8)
        self.bline.set_shader(uv_shader)
        self.bline.set_material((0.5,0.5,0.5))

        self.dial = pi3d.PolygonLines(camera=camera, vertices=dial_verts, line_width=8)
        self.dial.set_alpha(0.2)
        self.dial.set_shader(shader)

        font = pi3d.Font('opensans.ttf', codepoints='0123456789.-°', grid_size=5)
        self.actval = pi3d.PointText(font, camera, max_chars=10, point_size=100) 
        self.temp_block = pi3d.TextBlock(0, 0, 0.1, 0.0, 6, justify=0.5, text_format="0°", size=0.79,
                    spacing="F", space=0.02, colour=(1.0, 1.0, 1.0, 1.0))
        self.actval.add_text_block(self.temp_block)

        self.dot2= pi3d.Disk(radius=20, sides=20, z=0.1, rx=90, camera=camera)
        self.dot2.set_shader(shader)
        self.dot2.set_material((1, 1, 1))
        self.dot2_alpha = 1.0


        self.value = 25.0
        self.sensorvalue = 18.0
        degree = (self.angle_fr +  (self.angle_to - self.angle_fr) * (self.value - self.min_t)
                                                            / (self.max_t - self.min_t))
        self.x1 = self.mid * sin(radians(degree))
        self.y1 = self.mid * cos(radians(degree))



    def touch(self):
        try:
            time.sleep(0.001)
            data = self.bus.rdwr([0x40], 8, 0x5C)
            x1 = 400 - (data[0] | (data[4] << 8))
            y1 = (data[1] | (data[5] << 8)) - 240
            if y1 == 0:
                y1 = 1
            if ((-401 < x1 < 401) & (-241 < y1 < 241)):
                return x1, y1  # compensate position to match with PI3D
            else:
                time.sleep(0.01)
                return self.touch()
        except:
            time.sleep(0.05)
            return self.touch()

    def check_touch(self):
           if gpio.input(26):
            x3, y3 = self.touch()
            if ((self.x1 - 80) < x3 and x3  < (self.x1 + 80) and
                (self.y1 - 80) < y3 and y3  < (self.y1 + 80)):
                self.x1, self.y1 = x3, y3
                degree = int(degrees(atan2(self.x1, self.y1)))
                if degree < self.angle_fr:
                    degree = self.angle_fr
                if degree > self.angle_to:
                    degree = self.angle_to

                self.value = (self.min_t + (degree - self.angle_fr)
                             / (self.angle_to - self.angle_fr) * (self.max_t - self.min_t))
                sensordegree = (self.angle_fr +  (self.angle_to - self.angle_fr) * (self.sensorvalue - self.min_t)
                                                            / (self.max_t - self.min_t))
                if  self.value > self.sensorvalue:
                    self.ticks.set_material((1, 0 , 0))
                else:
                    self.ticks.set_material((0,0,1))
                """ move z values for shapes. The z tuple values represent:
                    0 to the set point (cut_n), 0 to the sensor point (cut_s),
                    between the two points, everwhere else. None prevents the section being adjusted
                    from a previously set value
                """
                updateelements = []

                updateelements.append((self.ticks, (-1.0, -1.0, 0.1, -1.0)))
                updateelements.append((self.sensorticks, (0.2, None, None, -1.0)))
                updateelements.append((self.dial, (-1.0, -1.0, 0.1, 0.1)))
                updateelements.append((self.bline, (None, 0.3, None, -1.0)))

                for (line_shape, z) in updateelements:
                    b = line_shape.buf[0]
                    v = b.array_buffer
                    cut_n = int((degree - self.angle_fr) / (self.angle_to - self.angle_fr) * len(v) / 4) * 4
                    if cut_n >= len(v):
                        cut_n = len(v) - 1
                    cut_s = int((sensordegree - self.angle_fr) / (self.angle_to - self.angle_fr) * len(v) / 4) * 4
                    if cut_s >= len(v):
                        cut_s = len(v) - 1
                    v[:, 2] = z[3]           # all set to the 'otherwise' value
                    if z[0] is not None:
                        v[:cut_s, 2] = z[0]  # set visibility up to sensor value
                    if z[1] is not None:
                        v[:cut_n, 2] = z[1]  # set vis up to set point value
                    if z[2] is not None:     # set between cut_n and cut_s
                        if cut_s > cut_n:
                            v[cut_n:cut_s, 2] = z[2]
                        else:
                            v[cut_s:cut_n, 2] = z[2]
                    b.re_init()
                    #b.set_material(rgb)

                self.temp_block.set_text(text_format="{:4.1f}°".format(self.value))
                self.actval.regen()

                self.x1 = self.mid * sin(radians(degree))
                self.y1 = self.mid * cos(radians(degree))

                self.dot2.position(self.x1, self.y1, 0.5)
                self.dot2_alpha = 1.0
                self.ticks_alpha = 0.0
                self.bline.draw()
            

    def draw(self):
        if self.dot2_alpha >= 0.0:
            self.dot2_alpha -= 0.01
            self.dot2.set_alpha(self.dot2_alpha)
            self.dot2.draw()
            if self.dot2_alpha < 0:
                self.temp_block.set_text(text_format="{:4.1f}°".format(self.sensorvalue))
                self.actval.regen()
                self.ticks_alpha = 0
        else:
            if self.ticks_alpha <= 1.0:
                self.ticks_alpha += 0.01
                self.ticks.set_alpha(self.ticks_alpha)
                if self.ticks_alpha >= 1.0:
                    self.ticks_alpha = 0.5

            self.ticks.draw()
        self.sensorticks.draw()
        self.dial.draw()
        self.actval.draw()

    def get_value(self):
        return self.value

    def set_value(self, value):
        self.value = value
        degree = (self.angle_fr +  (self.angle_to - self.angle_fr) * (self.value - self.min_t)
                                                            / (self.max_t - self.min_t))
        self.x1 = self.mid * sin(radians(degree))
        self.y1 = self.mid * cos(radians(degree))
        self.set_flag = True

DISPLAY = pi3d.Display.create(layer=0, w=800, h=480, background=(0.0, 0.0, 0.0, 1.0),
                              frames_per_second=60, tk=False, samples=4)
CAMERA = pi3d.Camera(is_3d=False) # will create its own cam if one not passed

dial = Dial(camera=CAMERA)

i = 0
while DISPLAY.loop_running():
    dial.check_touch()
    dial.draw()

DISPLAY.destroy()
