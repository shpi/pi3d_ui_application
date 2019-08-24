
#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys,os

import pi3d

sys.path.insert(1, os.path.join(sys.path[0], '..'))

import config
import core.graphics as graphics
import core.peripherals as peripherals




text3 = pi3d.PointText(graphics.pointFont, graphics.CAMERA, max_chars=820, point_size=64)    #slider3 Inputs


def add_to_text3(x, y, n_ch, text_format, attr=None, space=0.6, colour=(1.0, 1.0, 1.0, 1.0)):
  '''convenience function to avoid too much repitition'''
  newtxt = pi3d.TextBlock(x, y, 0.1, 0.0, n_ch, data_obj=peripherals.eg_object, attr=attr, text_format=text_format,
                          size=0.5, spacing="C", space=space, colour=colour)
  text3.add_text_block(newtxt)

add_to_text3(-380, 210, 22, text_format="HDD USED: {:s}", attr="useddisk")
add_to_text3(-380, 180, 25, text_format="FREE MB: {:2.0f}", attr="freespace")
add_to_text3(-380, 150, 22, text_format="LOAD:     {:2.1f}", attr="load")

add_to_text3(-380, 120, 22, text_format="WIFI SIG: {:s}dbm", attr="wifistrength")


#add_to_text3(-380, 90, 25, text_format= "IP:{:s}", attr="ipaddress")
#add_to_text3(-380, 60, 22, text_format= "SSID:     {:s}", attr="ssid")

add_to_text3(-380, 90, 22, text_format= "GPU TEMP: {:2.1f}", attr="gputemp")
add_to_text3(-380, 60, 22, text_format=  "CPU TEMP: {:2.1f}", attr="cputemp")
add_to_text3(-380, 30, 22, text_format="Voltage:  {:3d}mV", attr="atmega_volt")
add_to_text3(-380, 0, 22, text_format="Backlight:{:3d}", attr="backlight_level")
add_to_text3(-380,-30, 22, text_format= "Vent RPM: {:3d}", attr="vent_rpm")
add_to_text3(-380,-60, 22, text_format="Vent PWM: {:3d}", attr="vent_pwm")
add_to_text3(-380,-120, 22, text_format="AVR RAM:  {:3d}B", attr="atmega_ram")
add_to_text3(-380,-150, 22, text_format="Humidity: {:2.1f}%", attr="humidity")
if hasattr(peripherals.eg_object,'pressure'):
 add_to_text3(-380,-180, 22, text_format="Pressure: {:2.1f}hPa", attr="pressure")
 add_to_text3(-380, -210, 20, text_format="BMP280:   {:2.1f}", attr="bmp280_temp")
if hasattr(peripherals.eg_object,'lightlevel'):

 add_to_text3(-50, 210, 20, text_format= "LightLvl: {:2.1f}lx", attr="lightlevel")

add_to_text3(-50, 180, 20, text_format="SHT30:    {:2.1f}", attr="sht_temp")

add_to_text3(-50, 120, 20, text_format="ATmega:   {:2.1f}", attr="atmega_temp")
add_to_text3(-50, 90, 20, text_format="MLX A:    {:2.1f}", attr="mlxamb")
add_to_text3(-50, 60, 20, text_format= "MLX O:    {:2.1f}", attr="mlxobj")
add_to_text3(-50, 30, 20, text_format= "LED:", space=0.5)

add_to_text3(0, 30, 20, text_format="{:3d}", attr="led_red", colour=(1.0, 0.0, 0.0, 1.0))
add_to_text3(50, 30, 20, text_format="{:3d}", attr="led_green", colour=(0.0, 1.0, 0.0, 1.0))
add_to_text3(100, 30, 20, text_format="{:3d}", attr="led_blue", colour=(0.0, 0.0, 1.0, 1.0))


add_to_text3(-50, 0, 20, text_format=  "R1:    {:1d}", attr="relais1")
add_to_text3(-50, -30, 20, text_format= "R2:    {:1d}", attr="relais2")
add_to_text3(-50, -60, 20, text_format= "R3:    {:1d}", attr="relais3")
add_to_text3(-50, -90, 20, text_format= "D13:   {:1d}", attr="d13")
add_to_text3(-50, -120, 20, text_format="HWB:   {:1d}", attr="hwb")
add_to_text3(-50, -150, 20, text_format="Buzzer:{:1d}", attr="buzzer")

add_to_text3(120, 0, 20, text_format=  "A0:    {:3d}", attr="a0")
add_to_text3(120, -30, 20, text_format= "A1:    {:3d}", attr="a1")
add_to_text3(120, -60, 20, text_format= "A2:    {:3d}", attr="a2")
add_to_text3(120, -90, 20, text_format= "A3:    {:3d}", attr="a3")
add_to_text3(120, -120, 20, text_format="A4:    {:3d}", attr="a4")
add_to_text3(120, -150, 20, text_format="A5:    {:3d}", attr="a5")
add_to_text3(120, -180, 20, text_format="A7:    {:3d}", attr="a7")

add_to_text3(50, -210, 20, text_format="Current R1:{:2.1f}A", attr="relais1current")


background = pi3d.Sprite(camera=graphics.CAMERA,w=780,h=460,z=2, x = 0, y = 0)
background.set_shader(graphics.MATSH)
background.set_material((0.0, 0.0, 0.0))
background.set_alpha(0.7)



def inloop(textchange = False,activity = False, offset = 0):
 
    if textchange:
       text3.regen()
    if offset != 0:
        offset = graphics.slider_change(text3.text, offset)
        if offset == 0:
           text3.regen()
    background.draw()
    text3.draw()

    return activity,offset
