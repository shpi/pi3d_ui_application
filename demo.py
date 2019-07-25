#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import random,time, os , sys, smbus
import pi3d
import RPi.GPIO as gpio
import subprocess
from random import randint
import rrdtool
import numpy as np
import math

INFRARED_TM = 5
SENSOR_TM = 60

if not os.path.isfile('temperatures.rrd'):
  rrdtool.create(
    "temperatures.rrd",
    "--step","60",
    "DS:act_temp:GAUGE:120:-127:127",
    "DS:gpu:GAUGE:120:-127:127",
    "DS:cpu:GAUGE:120:-127:127",
    "DS:atmega:GAUGE:120:-127:127",
    "DS:sht:GAUGE:120:-127:127",
    "DS:bmp280:GAUGE:120:-127:127",
    "DS:mlxamb:GAUGE:120:-127:127",
    "DS:mlxobj:GAUGE:120:-127:127",
    "DS:ntc:GAUGE:120:-127:127",
    "RRA:MAX:0.5:1:1500",
    "RRA:MAX:0.5:10:1500",
    "RRA:MAX:0.5:60:1500")

# make 4M ramdisk for graph
os.popen('sudo mkdir /media/ramdisk')
os.popen('sudo mount -t tmpfs -o size=4M tmpfs /media/ramdisk')

controls_alpha = 1.0              # hide controls if there is no touch action
TOUCHINT = 26
TOUCHADDR = 0x5c
ADDR_32U4 = 0x2A
ADDR_BMP = 0x77
ADDR_SHT = 0x44
ADDR_MLX = 0x5B
ADDR_BH1750 = 0x23
PIR = 18
BACKLIGHT = 19 #single wire backlight control needs almost realtime -> moved to atmega  (not on prototypes, needs bit soldering, ask lh@shpi.de)

infrared_vals = np.full(100, np.nan)    # save 500seconds of infrared temperature for calculating room temp init to NaN

show_airquality = 1 # show airquality over LED
slide = 1                    #startslide
lastmovex = 0           #not needed for fakesliding. we still try to slide all text elements

touch_pressed = False  #will be set in interrupt routine
xc = 0  #last touchvars for integritychecks due to clockstretch errors and bitflips in i2c communication
yc = 0
lastx = 0
lasty = 0
lastmotion = 0
graphupdated = 0
nextsensorcheck = 0
everysecond = 0
nexttm = 0
user_temp_change = False  #for future use: if user change temp on touchscreen, save it in databank, otherwise load temp set from databank
motion = False

gpio.setmode(gpio.BCM)
gpio.setwarnings(False)
gpio.setup(TOUCHINT, gpio.IN)
gpio.setup(PIR, gpio.IN)
bus = smbus.SMBus(2)

def motion_detected(channel):  #try to catch bounce effects, stretch clock errors and bit flips, easiest: we need to have two identical measurements
  global motion
  if gpio.input(PIR):
    motion = True
    lastmotion = time.time()
  else:
    motion = False
    lastmotion = time.time()

def get_touch():
  global xc,yc
  if TOUCHADDR:     
   try:
         data = bus.read_i2c_block_data(TOUCHADDR, 0x40, 8)
         x1 = data[0] | (data[4] << 8)
         y1 = data[1] | (data[5] << 8)

         if ((-1 < x1  < 801) & (-1 < y1  < 481)):
          if ((-20 < (xc-x1) < 20) & (-20 < (yc-y1) < 20)):  #catch bounches 
           xc = x1
           yc = y1
           #print(x1,y1)
           return (400 - x1),(y1 - 240)  #compensate position to match with PI3D
          else:
           xc = x1
           yc = y1
           
           #print('not identical')
           return get_touch()
         else:
          return get_touch()


   except:
       time.sleep(0.03)  #wait on  I2C error
       #print('i2cerror')
       return get_touch() 
       pass    
       
  else:
    return 0,0       
       


def touch_debounce(channel):  
 global lastx, lasty, touch_pressed
 x,y = get_touch()
 if (channel == TOUCHINT):
  touch_pressed = True  
  lastx = x
  lasty = y
 else:
  return x,y;

gpio.add_event_detect(TOUCHINT, gpio.RISING, callback=touch_debounce, bouncetime=100)                                  #touch interrupt
gpio.add_event_detect(PIR, gpio.BOTH, callback=motion_detected, bouncetime=500)  #motion detector interrupt


try:
 bus.write_byte_data(TOUCHADDR,0x6e,0b00001110)                                              # interrupt configuration i2c
 bus.write_byte_data(TOUCHADDR,0x70,0b00000000)
except:
 print('no touchscreen found')
 TOUCHADDR = False
 pass

try:
  bus.write_byte(ADDR_32U4, 0x00)
except:
  ADDR_32U4 = False
  print('no ATmega found, seems to be a SHPI.zero lite?')
  pass

try:
 bus.write_byte(ADDR_SHT, 0x00)


except:
 ADDR_SHT = False
 print('no SHT found')
 pass

try:
 bus.write_byte(ADDR_BH1750, 0x00)


except:
 ADDR_BH1750 = False
 print('no BH1750 found')
 pass


try:
 bus.write_byte(ADDR_MLX, 0x00)
except:
 ADDR_MLX = False
 print('no MLX90615 found')
 pass

# correction values for BMP280
try:
  b1 = bus.read_i2c_block_data(ADDR_BMP, 0x88, 24)
  dig_T = [b1[i+1] * 256 + b1[i] for i in range(0, 6, 2)]
  dig_P = [b1[i+1] * 256 + b1[i] for i in range(6, 23, 2)]
  for i in range(1, len(dig_T)):
    if dig_T[i] > 32767:
      dig_T[i] -= 65536
  for i in range(1, len(dig_P)):
    if dig_P[i] > 32767:
      dig_P[i] -= 65536

except:
  print('no bmp280')
  ADDR_BMP = 0
  pass

PIC_DIR = './backgrounds'
TMDELAY = 30  #delay for changing backgrounds


def get_files():
  global SHUFFLE, PIC_DIR
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


class EgClass(object):
  set_temp = 23.0
  atmega_volt = 0
  backlight_level = 0
  mlxamb = 0.0
  mlxobj = 0.0
  bmp280_temp = 0.0
  sht_temp = 0.0
  gputemp =  0
  cputemp =  0
  atmega_temp = 0
  act_temp = 23.0
  useddisk = "0%"
  load = 0.0
  freespace = 0.0
  wifistrength = " "
  ipaddress = " "
  led_red = 0
  led_green = 0
  led_blue = 0
  vent_rpm = 0
  vent_pwm = 0
  ssid = " "
  uhrzeit = "00:00"
  atmega_ram = 0
  humidity = 0.0
  pressure = 0.0
  relais1 = 0
  relais2 = 0
  relais3 = 0
  d13 = 0
  hwb = 0
  a0 = 0
  a2 = 0
  a3 = 0
  a4 = 0
  a5 = 0
  a7 = 0
  buzzer = 0
  a1 = 0

eg_object = EgClass()

def read_one_byte(addr_val): # utility function for brevity
  bus.write_byte(ADDR_32U4, addr_val)
  return bus.read_byte(ADDR_32U4)

def read_two_bytes(addr_val): # utility function for brevity
  bus.write_byte(ADDR_32U4, addr_val)
  return bus.read_byte(ADDR_32U4) | (bus.read_byte(ADDR_32U4) << 8)

def get_sensors(): #readout all sensor values, system, and atmega vars
  global nextsensorcheck, slide, infrared_vals
  try:
    eg_object.useddisk = os.popen("df | grep root  | awk '{print $5}'").readline().strip()
    eg_object.uhrzeit = time.strftime("%H:%M")
    eg_object.load =  float(os.getloadavg()[0])
    s = os.statvfs('/')
    eg_object.freespace = float((s.f_bavail * s.f_frsize) / 1024 / 1024)
    eg_object.wifistrength = (os.popen("/sbin/iwconfig wlan0 | grep 'Signal level' | awk '{print $4}' | cut -d= -f2 | cut -d/ -f1;").readline()).strip()
    eg_object.ipaddress = os.popen("ip addr show wlan0 | grep 'inet ' | head -1 | awk '{print $2}' | cut -d/ -f1;").readline().strip()
    eg_object.gputemp = float(os.popen("vcgencmd measure_temp").readline()[5:-3])
    eg_object.cputemp = float(os.popen("cat /sys/class/thermal/thermal_zone0/temp").readline()) / 1000
    eg_object.ssid = (os.popen("/sbin/iwconfig wlan0 | grep \"SSID:\" | awk \"{print $4}\" | cut -d'\"' -f2").readline()).strip()
    if ADDR_32U4:
     eg_object.backlight_level = read_one_byte(0x07)
     eg_object.vent_pwm = read_one_byte(0x13)
     eg_object.relais1 = read_one_byte(0x0D)
     eg_object.relais2 = read_one_byte(0x0E)
     eg_object.relais3 = read_one_byte(0x0F)
     eg_object.d13 = read_one_byte(0x10)
     eg_object.hwb = read_one_byte(0x11)
     eg_object.buzzer = read_one_byte(0x12)

     eg_object.vent_rpm = read_two_bytes(0x08)
     eg_object.atmega_temp = read_two_bytes(0x0A) * 0.558 - 142.5
     eg_object.atmega_volt = read_two_bytes(0x09)
     eg_object.atmega_ram =  read_two_bytes(0x0B)
     eg_object.a0 = read_two_bytes(0x00)
     eg_object.a1 = read_two_bytes(0x01)
     eg_object.a2 = read_two_bytes(0x02)
     eg_object.a3 = read_two_bytes(0x03)
     eg_object.a4 = read_two_bytes(0x04)

     if show_airquality:
      redvalue = int(0.03 * eg_object.a4)
      if (eg_object.a4 > 400):
        greenvalue = 0
      else:
        greenvalue = int(0.02*(400 - eg_object.a4))
      bus.write_i2c_block_data(ADDR_32U4, 0x8C, [redvalue,greenvalue,0])

     bus.write_byte(ADDR_32U4, 0x0C)
     eg_object.led_red   = bus.read_byte(ADDR_32U4)
     eg_object.led_green = bus.read_byte(ADDR_32U4)
     eg_object.led_blue  = bus.read_byte(ADDR_32U4)

     eg_object.a5 = read_two_bytes(0x05)
     eg_object.a7 = read_two_bytes(0x06)
     
     
    if ADDR_SHT:
     bus.write_i2c_block_data(ADDR_SHT, 0x2C, [0x06])
     time.sleep(0.01)
     data = bus.read_i2c_block_data(ADDR_SHT, 0x00, 6)
     eg_object.sht_temp = float(((((data[0] * 256.0) + data[1]) * 175) / 65535.0) - 45)
     eg_object.humidity = 100 * (data[3] * 256 + data[4]) / 65535.0
     
     
    if ADDR_BMP:
      bus.write_byte_data(ADDR_BMP, 0xF4, 0x27)
      bus.write_byte_data(ADDR_BMP, 0xF5, 0xA0)
      data = bus.read_i2c_block_data(ADDR_BMP, 0xF7, 8)
      adc_p = ((data[0] * 65536) + (data[1] * 256) + (data[2] & 0xF0)) / 16
      adc_t = ((data[3] * 65536) + (data[4] * 256) + (data[5] & 0xF0)) / 16
      adc_h = data[6] * 256 + data[7]
      var1 = ((adc_t) / 16384.0 - (dig_T[0]) / 1024.0) * (dig_T[1])
      var2 = (((adc_t) / 131072.0 - (dig_T[0]) / 8192.0) * ((adc_t)/131072.0 - (dig_T[0])/8192.0)) * (dig_T[2])
      t_fine = (var1 + var2)
      eg_object.bmp280_temp = float((var1 + var2) / 5120.0)

      var1 = (t_fine / 2.0) - 64000.0
      var2 = var1 * var1 * (dig_P[5]) / 32768.0
      var2 = var2 + var1 * (dig_P[4]) * 2.0
      var2 = (var2 / 4.0) + ((dig_P[3]) * 65536.0)
      var1 = ((dig_P[2]) * var1 * var1 / 524288.0 + ( dig_P[1]) * var1) / 524288.0
      var1 = (1.0 + var1 / 32768.0) * (dig_P[0])
      p = 1048576.0 - adc_p
      p = (p - (var2 / 4096.0)) * 6250.0 / var1
      var1 = (dig_P[8]) * p * p / 2147483648.0
      var2 = p * (dig_P[7]) / 32768.0
      eg_object.pressure = (p + (var1 + var2 + (dig_P[6])) / 16.0) / 100

    eg_object.act_temp = np.nanmedian(infrared_vals)

    nextsensorcheck = (time.time() + SENSOR_TM)
    activity = True
    temperatures_str = 'N:{:.2f}:{:.2f}:{:.2f}:{:.2f}:{:.2f}:{:.2f}:{:.2f}:{:.2f}:{:.2f}'.format(
      eg_object.act_temp, eg_object.gputemp, eg_object.cputemp, eg_object.atmega_temp,
      eg_object.sht_temp, eg_object.bmp280_temp, eg_object.mlxamb, eg_object.mlxobj,(0.0))

    rrdtool.update('temperatures.rrd', temperatures_str)
    print(temperatures_str)

    '''
  [-c|--color COLORTAG#rrggbb[aa]]
  Override the default colors for the standard elements of the graph.
  BACK background,
  CANVAS for the background of the actual graph,
  SHADEA for the left and top border,
  SHADEB for the right and bottom border,
  GRID, MGRID for the major grid,
  FONT for the color of the font,
  AXIS for the axis of the graph,
  FRAME for the line around the color spots
  ARROW for the arrow head pointing up and forward.
  A green arrow is made by: --color ARROW#00FF00 A A
    '''
  except:
    pass

# chars and symbols for GUI

mytext = '1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZüöäÜÖÄ,.%:° -'
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
              chr(0xE013), #child
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
              chr(0xE020), #socket
              chr(0xE021), #temp
              #chr(0xE022), #tesla
              #chr(0xE023), #raspi
              #chr(0xE024), #privacy
              #chr(0xE025), #circle2
              #chr(0xE026), #bell
              #chr(0xE027), #nobell
              #chr(0xE028), #moon
              #chr(0xE029), #freeze
              #chr(0xE02A), #whatsapp
              #chr(0xE02B), #touch
              chr(0xE02C), #settings2
              #chr(0xE02D), #storm
              chr(0xE035), #shutter
              #chr(0xE034), #doublearrow
              #chr(0xE033), #usb
              #chr(0xE032), #magnet
              chr(0xE031), #phone
              #chr(0xE030), #compass
              #chr(0xE02E), #trash
              chr(0xE02F)] #cam


DISPLAY = pi3d.Display.create(layer=0,w=800, h=480,background=(0.0, 0.0, 0.0, 1.0),frames_per_second=60, tk=False)
shader = pi3d.Shader("uv_flat")
CAMERA = pi3d.Camera(is_3d=False)

def tex_load(fname):
  slide = pi3d.ImageSprite(fname,shader=shader,camera=CAMERA,w=800,h=480,z=2)
  slide.set_alpha(0)
  return slide

sfg = tex_load(iFiles[pic_num])

pointFont = pi3d.Font("opensans.ttf", shadow=(0, 0, 0, 255), shadow_radius=5, grid_size=11,
                       codepoints=mytext, add_codepoints=additional)
pointFontbig = pi3d.Font("opensans.ttf", shadow=(0, 0, 0, 255), shadow_radius=4, grid_size=5, codepoints='0123456789:')

#slide 0 (backgrounds off for camera)
str1 = pi3d.FixedString('opensans.ttf', 'Loading stream', font_size=32, background_color=(0,0,0,0),camera=CAMERA, shader=shader)
str1.sprite.position(0, 0, 0.1)
str2 = pi3d.FixedString('opensans.ttf', 'Touch to close stream.', font_size=22, background_color=(0,0,0,0), camera=CAMERA, shader=shader)
str2.sprite.position(0, -225, 0.1)
str3 = pi3d.FixedString('opensans.ttf', chr(0xE017), font_size=200, background_color=(0,0,0,0), camera=CAMERA, shader=shader)
str3.sprite.position(320, -120, 0.0)
str5 = pi3d.FixedString('opensans.ttf', chr(0xE017), font_size=200, background_color=(0,0,0,0), color=(255,0,0,255), camera=CAMERA, shader=shader)
str5.sprite.position(320, -120, 0.0)
str4 = pi3d.FixedString('opensans.ttf', chr(0xE026), font_size=200, background_color=(0,0,0,0), camera=CAMERA, shader=shader)
str4.sprite.position(320, 50, 0.0)

text = pi3d.PointText(pointFont, CAMERA, max_chars=220, point_size=128)    #slide 1
text2 = pi3d.PointText(pointFontbig, CAMERA, max_chars=20, point_size=256)   #slide 2
text3 = pi3d.PointText(pointFont, CAMERA, max_chars=800, point_size=64)   #slide 3

slide_offset = 0 # change by touch and slide

#slider1

temp_block = pi3d.TextBlock(-350, 130, 0.1, 0.0, 15, data_obj=eg_object,attr="act_temp",text_format= chr(0xE021) +"{:2.1f}°C", size=0.99, spacing="F", space=0.05, colour=(1.0, 1.0, 1.0, 1.0))
text.add_text_block(temp_block)
set_temp_block= pi3d.TextBlock(-330, 50, 0.1, 0.0, 15, data_obj=eg_object,text_format= chr(0xE005) + " {:2.1f}°C", attr="set_temp",size=0.5, spacing="F", space=0.05, colour=(1.0, 1.0, 1.0, 1.0))
text.add_text_block(set_temp_block)
increaseTemp = pi3d.TextBlock(300, 150, 0.1, 180.0, 1, text_format= chr(0xE000),size=0.99, spacing="C", space=0.6, colour=(1, 0, 0, 0.8))
text.add_text_block(increaseTemp)
decreaseTemp = pi3d.TextBlock(300, -50, 0.1, 0.0, 1, text_format= chr(0xE000),size=0.99, spacing="C", space=0.6, colour=(0, 0, 1, 0.8))
text.add_text_block(decreaseTemp)

newtxt = pi3d.TextBlock(270, -180, 0.1, 0.0, 15, text_format = chr(0xE001), size=0.99, spacing="F", space=0.05, colour = (1.0, 1.0, 1.0, 1.0))
text.add_text_block(newtxt)
motiondetection = pi3d.TextBlock(290, -175, 0.1, 0.0, 15, text_format = chr(0xE01C), size=0.79, spacing="F", space=0.05, colour = (1.0, 1.0, 1.0, 1.0))
text.add_text_block(motiondetection)
newtxt = pi3d.TextBlock(145, -180, 0.1, 0.0, 15, text_format = chr(0xE001), size=0.99, spacing="F", space=0.05, colour = (1.0, 1.0, 1.0, 1.0))
text.add_text_block(newtxt)
heating = pi3d.TextBlock(170, -180, 0.1, 0.0, 15, text_format = chr(0xE004), size=0.79, spacing="F", space=0.05, colour = (1.0, 1.0, 1.0, 1.0))
text.add_text_block(heating)
newtxt = pi3d.TextBlock(-400, -180, 0.1, 0.0, 15, text_format = chr(0xE001), size=0.99, spacing="F", space=0.05, colour = (1.0, 1.0, 1.0, 1.0))
text.add_text_block(newtxt)
newtxt = pi3d.TextBlock(-385, -180, 0.1, 0.0, 15, text_format = chr(0xE02F), size=0.79, spacing="F", space=0.05, colour = (1.0, 1.0, 1.0, 1.0))
text.add_text_block(newtxt)
newtxt = pi3d.TextBlock(-300, -180, 0.1, 0.0, 15, text_format = chr(0xE001), size=0.99, spacing="F", space=0.05, colour = (1.0, 1.0, 1.0, 1.0))
text.add_text_block(newtxt)
newtxt = pi3d.TextBlock(-275, -180, 0.1, 0.0, 15, text_format = chr(0xE031), size=0.79, spacing="F", space=0.05, colour = (1.0, 1.0, 1.0, 1.0))
text.add_text_block(newtxt)

# slider2
uhrzeit_block = pi3d.TextBlock(-280, 0, 0.1, 0.0, 15, data_obj=eg_object,attr="uhrzeit", text_format= "{:s}", size=0.99, spacing="F", space=0.05, colour=(1.0, 1.0, 1.0, 1.0))
text2.add_text_block(uhrzeit_block)

#slider3: still needs to be formated, but chars uses different width, need to change font or split strings in vars and identifiers
def add_to_text3(x, y, n_ch, text_format, attr=None, space=0.6, colour=(1.0, 1.0, 1.0, 1.0)):
  '''convenience function to avoid too much repitition'''
  newtxt = pi3d.TextBlock(x, y, 0.1, 0.0, n_ch, data_obj=eg_object, attr=attr, text_format=text_format,
                          size=0.5, spacing="C", space=space, colour=colour)
  text3.add_text_block(newtxt)

add_to_text3(-390, 210, 22, text_format="HDD USED: {:s}", attr="useddisk")
add_to_text3(-390, 180, 25, text_format="FREE MB: {:2.0f}", attr="freespace")
add_to_text3(-390, 150, 22, text_format="LOAD:     {:2.1f}", attr="load")
add_to_text3(-390, 120, 22, text_format="WIFI SIG: {:s}dbm", attr="wifistrength")
add_to_text3(-390, 90, 25, text_format= "IP:{:s}", attr="ipaddress")
add_to_text3(-390, 60, 22, text_format= "SSID:     {:s}", attr="ssid")
add_to_text3(-390, 30, 22, text_format= "GPU TEMP: {:2.1f}", attr="gputemp")
add_to_text3(-390, 0, 22, text_format=  "CPU TEMP: {:2.1f}", attr="cputemp")
add_to_text3(-390, -30, 22, text_format="Voltage:  {:3d}mV", attr="atmega_volt")
add_to_text3(-390, -60, 22, text_format="Backlight:{:3d}", attr="backlight_level")
add_to_text3(-390,-90, 22, text_format= "Vent RPM: {:3d}", attr="vent_rpm")
add_to_text3(-390,-120, 22, text_format="Vent PWM: {:3d}", attr="vent_pwm")
add_to_text3(-390,-150, 22, text_format="AVR RAM:  {:3d}", attr="atmega_ram")
add_to_text3(-390,-180, 22, text_format="Humidity: {:2.1f}", attr="humidity")
add_to_text3(-390,-210, 22, text_format="Pressure: {:2.1f}", attr="pressure")

add_to_text3(-50, 190, 20, text_format="SHT30:    {:2.1f}", attr="sht_temp")
add_to_text3(-50, 160, 20, text_format="BMP280:   {:2.1f}", attr="bmp280_temp")
add_to_text3(-50, 130, 20, text_format="ATmega:   {:2.1f}", attr="atmega_temp")
add_to_text3(-50, 100, 20, text_format="MLX A:    {:2.1f}", attr="mlxamb")
add_to_text3(-50, 70, 20, text_format= "MLX O:    {:2.1f}", attr="mlxobj")
add_to_text3(-50, 40, 20, text_format= "LED:", space=0.5)

add_to_text3(0, 40, 20, text_format="{:3d}", attr="led_red", colour=(1.0, 0.0, 0.0, 1.0))
add_to_text3(50, 40, 20, text_format="{:3d}", attr="led_green", colour=(0.0, 1.0, 0.0, 1.0))
add_to_text3(100, 40, 20, text_format="{:3d}", attr="led_blue", colour=(0.0, 0.0, 1.0, 1.0))

add_to_text3(-50, 10, 20, text_format=  "R1:    {:1d}", attr="relais1")
add_to_text3(-50, -20, 20, text_format= "R2:    {:1d}", attr="relais2")
add_to_text3(-50, -50, 20, text_format= "R3:    {:1d}", attr="relais3")
add_to_text3(-50, -80, 20, text_format= "D13:   {:1d}", attr="d13")
add_to_text3(-50, -110, 20, text_format="HWB:   {:1d}", attr="hwb")
add_to_text3(-50, -140, 20, text_format="Buzzer:{:1d}", attr="buzzer")

add_to_text3(120, 10, 20, text_format=  "A0:    {:3d}", attr="a0")
add_to_text3(120, -20, 20, text_format= "A1:    {:3d}", attr="a1")
add_to_text3(120, -50, 20, text_format= "A2:    {:3d}", attr="a2")
add_to_text3(120, -80, 20, text_format= "A3:    {:3d}", attr="a3")
add_to_text3(120, -110, 20, text_format="A4:    {:3d}", attr="a4")
add_to_text3(120, -140, 20, text_format="A5:    {:3d}", attr="a5")
add_to_text3(120, -170, 20, text_format="A7:    {:3d}", attr="a7")

def slider_change(shape_obj, offset_val):
  abs_offset = abs(offset_val)
  if abs_offset > 0: # only do something if offset
    if abs_offset < 6: # needs to be > min move distance
      offset_val = 0
    else:
      speed = min(20, max(5, abs_offset * 0.1))
      offset_val -= math.copysign(speed, offset_val)
    shape_obj.positionX(-offset_val)
  return offset_val # rather than using a global or passing ref to change




while DISPLAY.loop_running():
  if (time.time() > everysecond):
    everysecond = time.time() + INFRARED_TM
    if ADDR_MLX:
     try:
      eg_object.mlxamb = float((bus.read_word_data(ADDR_MLX, 0x26) *0.02)  - 273.15)
      eg_object.mlxobj = float((bus.read_word_data(ADDR_MLX, 0x27) *0.02)  - 273.15)
      infrared_vals [:-1] = infrared_vals[1:]
      if (eg_object.mlxamb > eg_object.mlxobj):                                   # compensate own self heating
        infrared_vals[-1] = eg_object.mlxobj -  ((eg_object.mlxamb - eg_object.mlxobj) / 6)
      else:
        infrared_vals[-1] = eg_object.mlxobj

     except:
      pass

  if (time.time() > nextsensorcheck):
    get_sensors()

  if slide > 0:

    if time.time() > nexttm:                                     # change background
      nexttm = time.time() + TMDELAY
      a = 0.0
      sbg = sfg
      sbg.positionZ(3)
      pic_num = (pic_num + 1) % nFi
      sfg = tex_load(iFiles[pic_num])

    if a < 1.0:                                              # fade to new background
      activity = True  #we calculate   more frames, when there is activity, otherwise we add sleep.time at end
      a += 0.02
      sbg.draw()
      sfg.set_alpha(a)

    sfg.draw()

  if controls_alpha > 0.3:                                              # control elements alpha
    controls_alpha -= 0.01

  if gpio.input(TOUCHINT):                              # check if touch is pressed, to detect sliding
    x,y = get_touch()
    if ((x != 0) and lastx):
      movex = (lastx - x)
      movey = (lasty - x)
      if (abs(movex) > 10):                              #calculate slider movement
        slide_offset = movex
        activity = True
  else:
    movex = 0

  if movex < -300 and slide > 1:     #start sliding when there is enough touchmovement     
    lastx = 0
    movex = 0
    slide = slide - 1
    sbg.set_alpha(0)
    a = 0
    slide_offset += 400

  if movex > 300 and slide < 4:
    lastx = 0
    movex = 0
    slide = slide + 1
    sbg.set_alpha(0)
    a = 0
    slide_offset -= 400

  if slide == 0:
    str1.draw()
    str2.draw()
    if  touch_pressed:
      touch_pressed = False
      os.popen('killall omxplayer.bin')
      slide = 1

  if slide == 4:
    if graphupdated < time.time():
      graphupdated = time.time() + 60
      #rrdtool.graph("graph1.png" ,"--full-size-mode","--font","DEFAULT:13:","--color","BACK#ffffffC0","--color","CANVAS#ffffff00","--color","SHADEA#ffffff00","--color","SHADEB#ffffff00","--width","800","--height","480","--start","-1h","--title","temperature overview","--vertical-label","°C",
      rrdtool.graph("/media/ramdisk/graph1.png" ,"--full-size-mode","--font","DEFAULT:13:","--color","BACK#ffffffC0","--color","CANVAS#ffffff00","--color","SHADEA#ffffff00","--color","SHADEB#ffffff00","--width","800","--height","480","--start","-1h","--title","temperature overview","--vertical-label","°C",
"DEF:act_temp=temperatures.rrd:act_temp:AVERAGE",
"DEF:cpu=temperatures.rrd:cpu:AVERAGE",
"DEF:gpu=temperatures.rrd:gpu:AVERAGE",
"DEF:atmega=temperatures.rrd:atmega:AVERAGE",
"DEF:sht=temperatures.rrd:sht:AVERAGE",
"DEF:bmp280=temperatures.rrd:bmp280:AVERAGE",
"DEF:mlxamb=temperatures.rrd:mlxamb:AVERAGE",
"DEF:mlxobj=temperatures.rrd:mlxobj:AVERAGE",
"LINE4:act_temp#ff0000:ROOM",
"LINE2:cpu#ff0000:CPU",
"LINE2:gpu#ff0000:GPU",
"LINE2:atmega#00ff00:AVR",
"LINE2:sht#0000ff:SHT30",
"LINE2:mlxamb#ff00ff:MLX_A",
"LINE2:mlxobj#00ffff:MLX_O",
"LINE2:bmp280#888800:BMP280")
      #graph = pi3d.ImageSprite('graph1.png',shader=shader,camera=CAMERA,w=800,h=480,z=1)
      graph = pi3d.ImageSprite('/media/ramdisk/graph1.png',shader=shader,camera=CAMERA,w=800,h=480,z=1)
    slide_offset = slider_change(graph, slide_offset)
    graph.draw()

  if slide == -1:
    str1.draw()
    str2.draw()
    str4.draw()
    if gpio.input(TOUCHINT):
      checkx = 400
      checky = -150
      if ((checkx-100) < x < (checkx+100)) and ((checky-100) < y < (checky+100)):
        str5.draw()

        #we deactivate speaker, while talking, to avaoid feedback and increase privacy for door intercoms
        #os.popen('amixer set Master 0%')
        #os.popen('amixer set Capture 100%')

    else:
      str3.draw()
      #os.popen('amixer set Master 100%')
      #os.popen('amixer set Capture 0%')
    if (touch_pressed and (lastx < 0)):        #only close if left side touched
      touch_pressed = False
      os.popen('killall nc') #warning just a test
      os.popen('killall ./videoplayer')
      os.popen('killall omxplayer.bin')
      os.popen('killall raspivid')
      slide = 1

  if (slide == 3):
    slide_offset = slider_change(text3.text, slide_offset)
    if activity:
      text3.regen()
    text3.draw()

  if slide == 1:
    if (motion):
      motiondetection.colouring.set_colour([1,0,0])
    else:
      motiondetection.colouring.set_colour([1,1,1])

    if touch_pressed:
      touch_pressed = False
      activity = True
      checkx = 300      #we describe touch areas manually, in future we could use object position values
      checky = 150
      if ((checkx-50) < lastx < (checkx+50)) and ((checky-50) < lasty < (checky+50)):
        eg_object.set_temp += 0.5
        user_temp_change = True
        set_temp_block.colouring.set_colour([1,0,0])
      checky = -40
      if ((checkx-50) < lastx < (checkx+50)) and ((checky-50) < lasty < (checky+50)):
        eg_object.set_temp -= 0.5
        user_temp_change = True
        set_temp_block.colouring.set_colour([0,0,1])

      checkx = -330
      checky = -180
      if ((checkx-50) < lastx < (checkx+50)) and ((checky-50) < lasty < (checky+50)):
        slide = 0
        try:
          os.popen('killall omxplayer.bin')
        except:
          pass
        os.popen('omxplayer --threshold 0.5  --display 4 rtsp://username:pass@192.168.1.5:554/mpeg4cif --win "0 0 800 450"')       # loading time depends on keyframes in stream, only h264 recommended!

      checkx = -230
      checky = -180
      if ((checkx-50) < lastx < (checkx+50)) and ((checky-50) < lasty < (checky+50)):
        slide = -1
        try:
          os.popen('killall omxplayer.bin')
          os.popen('killall raspivid')
        except:
          pass
        os.popen('sshpass -p \'raspberry\' ssh -o StrictHostKeyChecking=no  pi@192.168.1.34 "raspivid  -t 0 -w 640 -h 480 -g 10 -ih -fps 25 -l -p \'640,0,160,120\' -o  tcp://0.0.0.0:5001"')
        os.popen('raspivid  -t 0 -w 640 -h 480 -g 10  -ih -fps 25 -hf  -vf -l -p \'640,0,160,120\' -o  tcp://0.0.0.0:5002')
        os.popen('sleep 1 && nc 192.168.1.34 5001 | ./videoplayer 0 0 640 480')      
        os.popen('sshpass -p \'raspberry\' ssh -o StrictHostKeyChecking=no  pi@192.168.1.34 "nc 192.168.1.50 5002 | ./videoplayer 0 0 640 480"') 

        #intercom between 2 SHPIs,  just a test concept,  master access slave and start necessary applications
        #os.popen('arecord -D plughw:1,0 -r 8000 -f S16_LE -c1 -N -B 100 -t wav | nc -l 5002')
        #os.popen('nc [ownip] 5002 | aplay -f S16_LE -c1 -r 8000')
        #sshpass -p 'password' ssh -o StrictHostKeyChecking=no  user@server "raspivid  -t 0 -w 640 -h 480 -g 10 -if both -ih -fps 25 -l -p \'640,0,160,120\' -o  tcp://0.0.0.0:5001";
        #sshpass -p 'password' ssh -o StrictHostKeyChecking=no  user@server "arecord -D plughw:1,0 -r 8000 -f S16_LE -c1 -N -B 100 -t wav | nc -l 5002";
        #sshpass -p 'password' ssh -o StrictHostKeyChecking=no  user@server "nc [ownip] 5002 | aplay -f S16_LE -c1 -r 8000";
        #sshpass -p 'password' ssh -o StrictHostKeyChecking=no  user@server "omxplayer --win 0,0,640,480 tcp://[ip]:5000";

    if controls_alpha > 0.3:
      activity = True
      increaseTemp.colouring.set_colour(alpha = controls_alpha)
      decreaseTemp.colouring.set_colour(alpha = controls_alpha)
      set_temp_block.colouring.set_colour(alpha = controls_alpha)
    else:
      set_temp_block.colouring.set_colour([1,1,1])

    slide_offset = slider_change(text.text, slide_offset)
    if activity:
      text.regen()
    text.draw()

  if slide == 2:
    slide_offset = slider_change(text2.text, slide_offset)
    if activity:
      text2.regen()
    text2.draw()

  if activity:
    activity = False
  else:
    time.sleep(0.1)

DISPLAY.destroy()