#!/usr/bin/env python
# -*- coding: utf-8 -*-
import RPi.GPIO as gpio
import smbus
import sys
import numpy as np
import os
import time
import struct
import pi3d 

sys.path.insert(1, os.path.join(sys.path[0], '..'))
import config

if config.startmqttclient:
  import core.mqttclient as mqttclient



os_touchdriver = os.popen('pgrep -f touchdriver.py -c') #checks if touchdriver is running
if os_touchdriver: 

    print('os touch driver active')
    mouse = pi3d.Mouse(restrict=False)
    mouse.start()


xc, yc, lastx, lasty,touch_pressed,lasttouch = 0,0,0,0,0,0

VALS = { # various aliases for off and on
  '0': 0x00, 0: 0x00, 'OFF': 0x00,
  '1': 0xFF, 1: 0xFF, 'ON': 0xFF,
  'CLICK': 0x01,
}


READ_A0 = 0x00
READ_A1 = 0x01
READ_A2 = 0x02
READ_A3 = 0x03
READ_A4 = 0x04
READ_BACKLIGHT_LEVEL = 0x07
READ_VENT_RPM = 0x08
READ_ATMEGA_VOLT = 0x09
READ_D13 = 0x10
READ_HWB = 0x11
READ_BUZZER = 0x12
READ_VENT_PWM = 0x13
READ_RELAIS1CURRENT = 0x14
READ_ATMEGA_TEMP = 0x0A
READ_ATMEGA_RAM = 0x0B
READ_RELAIS1 = 0x0D
READ_RELAIS2 = 0x0E
READ_RELAIS3 = 0x0F
BACKLIGHT_LEVEL = 0x87
RELAIS1 = 0x8D
RELAIS2 = 0x8E
RELAIS3 = 0x8F
D13 = 0x90
BUZZER = 0x92
VENT_PWM = 0x93

RELAYCHANNEL = [0x8D, 0x8E, 0x8F, 0x92, 0x90]

TOUCHADDR = 0x5c
ADDR_32U4 = 0x2A
ADDR_BMP = 0x77
ADDR_SHT = 0x44
ADDR_MLX = 0x5B
ADDR_BH1750 = 0x23
PIR = 18
BACKLIGHT = 19 #single wire backlight control needs almost realtime -> moved to atmega  (not on prototypes!)
TOUCHINT = 26


bus = smbus.SMBus(2) 

try:
  bus.write_byte_data(TOUCHADDR, 0x6e, 0b00001110)                                              # interrupt configuration i2c
  bus.write_byte_data(TOUCHADDR, 0x70, 0b00000000)
except:
  print('no touchscreen found')
  TOUCHADDR = False


#check for atmega  -> future: lite or std SHPI
try:
  bus.write_byte(ADDR_32U4, 0x00)
except:
  ADDR_32U4 = False
  print('no ATmega found, seems to be a SHPI.zero lite?')


#check for SHT3x
try:
  bus.write_byte(ADDR_SHT, 0x00)
except:
  ADDR_SHT = False
  print('no SHT found')

#check for light sensor BH1750
try:
  bus.write_byte(ADDR_BH1750,0x01) #power on BH1750
except:
  print('no BH1750')
  ADDR_BH1750 = False



#check for MLX90615
try:
  bus.write_byte(ADDR_MLX, 0x00)
except:
  ADDR_MLX = False
  print('no MLX90615 found')

#correction values for BMP280
try:
   b1 = bytes(bus.read_i2c_block_data(ADDR_BMP, 0x88, 24))
   dig_T = struct.unpack_from('<Hhh', b1, 0)
   dig_P = struct.unpack_from('<Hhhhhhhhh', b1, 6)
except:
  print('no bmp280')
  ADDR_BMP = 0
     

class EgClass(object):

  if ADDR_32U4:
      atmega_volt = 0
      d13 = 0
      hwb = 0
      a0 = 0
      a1 = 0
      a2 = 0
      a3 = 0
      a4 = 0
      a5 = 0
      a7 = 0  
      atmega_temp = 0
      vent_rpm = 0
      vent_pwm = 0
      atmega_ram = 0
      buzzer = 0
      relais1current = 0.0
      
  if ADDR_MLX:     
      mlxamb = 0.0
      mlxobj = 0.0

  if ADDR_BMP:       
      bmp280_temp = 0.0 
      pressure = 0.0
      
  if ADDR_BH1750:
      lightlevel = 0.0
  
  if ADDR_SHT:
      sht_temp = 0.0
      humidity = 0.0
      
   
  motion = False
  set_temp = 23.0  
  backlight_level = 0

           
  gputemp =  0
  cputemp =  0
  act_temp = 0.0
  useddisk = "0%"
  load = 0.0
  freespace = 0.0
  wifistrength = " "
  ipaddress = " "
  led_red = 0
  led_green = 0
  led_blue = 0
  ssid = " "
  uhrzeit = "00:00"    
  relais1 = 0
  relais2 = 0
  relais3 = 0    
  lastmotion = time.time()
  max_backlight = config.max_backlight
  usertext = ''
  usertextshow = '|'
  alert =  0
  led = [led_red, led_green, led_blue]
eg_object = EgClass()

def alert(value = 1):
  if value and (int)(time.time())%2 == 0:
      controlrelays(4,1)
      controlled([255,0,0])
      controlbacklight(1)
      config.subslide = 'alert'
  else:
      controlrelays(4,0)
      controlled([0,0,0])
      controlbacklight(eg_object.max_backlight)

def touched():
  return gpio.input(TOUCHINT)  

def motion_detected(channel):  
  if gpio.input(channel): 
     eg_object.motion  = True
     if config.startmqttclient:
         mqttclient.publish("motion", 'ON')
  else: 
    eg_object.motion = False
    if config.startmqttclient:
         mqttclient.publish("motion", 'OFF')

  eg_object.lastmotion = time.time()

def get_touch():
  global  xc,yc, os_touchdriver, mouse
  if os_touchdriver:
   x1, y1 = mouse.position()
   x1 = 0.8 * x1
   y1 = 0.65 * y1
   if ((-401 < x1  < 401) & (-241 < y1  < 241)):
        if ((-80 < (xc-x1) < 80) & (-80 < (yc-y1) < 80)):  #catch bounches
          xc = x1
          yc = y1
          return xc, yc
        else: 
          return get_touch()
   else:
     return get_touch()
  elif TOUCHADDR:
    try:
      data = bus.read_i2c_block_data(TOUCHADDR, 0x40, 8)
      x1 = 400 - (data[0] | (data[4] << 8))
      y1 = (data[1] | (data[5] << 8)) - 240

      if ((-401 < x1  < 401) & (-241 < y1  < 241)):
        if ((-80 < (xc-x1) < 80) & (-80 < (yc-y1) < 80)):  #catch bounches
          xc = x1
          yc = y1
          #print(x1,y1)
         
          return x1,y1  #compensate position to match with PI3D
        else:
          xc = x1
          yc = y1

          print('not identical')
          return get_touch()
      else:
        return get_touch()


    except:
        time.sleep(0.06)  #wait on  I2C error
        print('i2cerror')
        return get_touch()

  else:
    return 0,0


def clicked(x,y):
  global lastx, lasty

  if ((x - 50) < lastx < (x + 50)) and  ((y - 50) < lasty < (y + 50)):
    return True
  else:
    return False



def touch_debounce(channel):
  global lastx, lasty, touch_pressed,lasttouch
  x,y = get_touch()
  lasttouch = time.time()
  if (channel == TOUCHINT):
    eg_object.lastmotion = time.time() # wake screen up on touch
    if ADDR_32U4:
      clicksound()
    touch_pressed = True
    lastx = x
    lasty = y



def clicksound():
  bus.write_byte_data(ADDR_32U4, BUZZER, VALS['CLICK'])
  

def controlrelays(channel, value, retries=0):
  try:
    bus.write_byte_data(ADDR_32U4, RELAYCHANNEL[channel-1], VALS[value])
   
  except Exception as e: # potential inifinite loop - count repeats and break after n
    print('error setting channels: {}'.format(e))
    if retries < 25:
      time.sleep(0.02)
      controlrelays(channel, value, retries + 1)
      
def read_one_byte(addr_val): # utility function for brevity
  bus.write_byte(ADDR_32U4, addr_val)
  return bus.read_byte(ADDR_32U4)

def read_two_bytes(addr_val): # utility function for brevity
  bus.write_byte(ADDR_32U4, addr_val)
  return bus.read_byte(ADDR_32U4) | (bus.read_byte(ADDR_32U4) << 8)
  
def controlvent(value):
    value = int(value) # variable int value
    assert -1 < value < 256, 'value outside 0..255'
    bus.write_byte_data(ADDR_32U4, 0x93, value)

def controlbacklight(value):
      os.popen('sudo chrt --rr 99 ' + config.installpath + 'bin/backlight {}'.format(value)) #needs sudo because of timing
      try:
       bus.write_byte_data(ADDR_32U4, BACKLIGHT_LEVEL, value)
      except:
       pass

def controlled(rgbvalues, retries=0):
    if len(rgbvalues) == 3:
      rgb = []
      for value in rgbvalues:
       value = int(value) # variable int value
       assert -1 < value < 256, 'value outside 0..255'
       rgb.append(value)
      try:
           bus.write_i2c_block_data(ADDR_32U4, 0x8C, rgb)
      except Exception as e: # potential inifinite loop - count repeats and break after n
           print('error setting channels: {}'.format(e))
           if retries < 25:
               time.sleep(0.02)
               controlled(rgbvalues,retries +1)
    else:
             print('error, wrong rgbvalues for controlled')
      
      
      ## cooling & heating function
      
def heating():
    if (eg_object.act_temp + config.HYSTERESIS) < eg_object.set_temp:
      controlrelays(config.heatingrelay, 1)
    
    elif (eg_object.act_temp - config.HYSTERESIS) > eg_object.set_temp:
      controlrelays(config.heatingrelay, 0)
      
      
def cooling():   
    if (eg_object.act_temp + config.HYSTERESIS) < eg_object.set_temp:
      controlrelays(config.coolingrelay, 1)
    elif (eg_object.act_temp - config.HYSTERESIS) > eg_object.set_temp:
      controlrelays(config.collingrelay, 0)
   
def coolingheating():   
    if eg_object.set_temp - config.HYSTERESIS < eg_object.act_temp < eg_object.set_temp + config.HYSTERESIS:       
      controlrelays(config.heatingrelay, 0)
    else:
      controlrelays(config.heatingrelay, 1)    

def get_infrared():

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


def get_status():
  try:
        eg_object.useddisk = os.popen("df | grep root  | awk '{print $5}'").readline().strip()
        eg_object.load =  float(os.getloadavg()[0])
        s = os.statvfs('/')
        eg_object.freespace = float((s.f_bavail * s.f_frsize) / 1024 / 1024)
        eg_object.wifistrength = (os.popen("/sbin/iwconfig wlan0 | grep 'Signal level' | awk '{print $4}' | cut -d= -f2 | cut -d/ -f1;").readline()).strip()
        eg_object.ipaddress = os.popen("ip addr show wlan0 | grep 'inet ' | head -1 | awk '{print $2}' | cut -d/ -f1;").readline().strip()
        eg_object.ssid = (os.popen("/sbin/iwconfig wlan0 | grep \"SSID:\" | awk \"{print $4}\" | cut -d'\"' -f2").readline()).strip()

        if ADDR_32U4:



           eg_object.backlight_level = read_one_byte(READ_BACKLIGHT_LEVEL)
           eg_object.vent_pwm = read_one_byte(READ_VENT_PWM)
           eg_object.relais1 = 1 if read_one_byte(READ_RELAIS1) == 255 else 0
           eg_object.relais2 = 1 if read_one_byte(READ_RELAIS2) == 255 else 0
           eg_object.relais3 = 1  if read_one_byte(READ_RELAIS3) == 255 else 0
           eg_object.d13 = 1 if read_one_byte(READ_D13) == 255 else 0
           eg_object.hwb = 1 if read_one_byte(READ_HWB) == 255 else 0
           eg_object.buzzer = 1 if read_one_byte(READ_BUZZER) == 255 else 0
           eg_object.vent_rpm = read_two_bytes(READ_VENT_RPM)
           eg_object.atmega_ram =  read_two_bytes(READ_ATMEGA_RAM)
           bus.write_byte(ADDR_32U4, 0x0C)
           eg_object.led_red   = bus.read_byte(ADDR_32U4)
           eg_object.led_green = bus.read_byte(ADDR_32U4)
           eg_object.led_blue  = bus.read_byte(ADDR_32U4)
           eg_object.led = led = [eg_object.led_red, eg_object.led_green, eg_object.led_blue]



  except:
   pass



def get_sensors(): #readout all sensor values, system, and atmega vars
  global infrared_vals,dig_T,dig_P
  
  try:
    
    eg_object.uhrzeit = time.strftime("%H:%M")
    eg_object.gputemp = float(os.popen("vcgencmd measure_temp").readline()[5:-3])
    eg_object.cputemp = float(os.popen("cat /sys/class/thermal/thermal_zone0/temp").readline()) / 1000

    if ADDR_SHT:
      bus.write_i2c_block_data(ADDR_SHT, 0x24, [0x00]) #clockstretching disabled , softreset: 0x30A2 or general call: 0x0006
      time.sleep(0.02)
      data = bus.read_i2c_block_data(ADDR_SHT, 0x00, 6)
      eg_object.sht_temp = float(((((data[0] * 256.0) + data[1]) * 175) / 65535.0) - 45)
      eg_object.humidity = 100 * (data[3] * 256 + data[4]) / 65535.0

    if ADDR_BH1750:
      data = bus.read_i2c_block_data(ADDR_BH1750,0x23)   #0x20 highres 1 lux prec.,  0x21 highres2 0.5lux prec., 0x23 4 lux prec. fast!
      eg_object.lightlevel = (float)((data[1] + (256 * data[0])) / 1.2)


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

    
    
    if ADDR_32U4:


      eg_object.relais1current = (((5000/1024) *
                              (read_one_byte(READ_RELAIS1CURRENT) - 2)) / 185)
      eg_object.atmega_temp = read_two_bytes(READ_ATMEGA_TEMP) * 0.558 - 142.5
      eg_object.atmega_volt = read_two_bytes(READ_ATMEGA_VOLT)
      eg_object.a0 = read_two_bytes(READ_A0)
      eg_object.a1 = read_two_bytes(READ_A1)
      eg_object.a2 = read_two_bytes(READ_A2)
      eg_object.a3 = read_two_bytes(READ_A3)
      eg_object.a4 = read_two_bytes(READ_A4)
      eg_object.a5 = read_two_bytes(0x05)
      eg_object.a7 = read_two_bytes(0x06)




  except Exception as e:
    print(e)      
      
      
gpio.setmode(gpio.BCM)
gpio.setwarnings(False)
gpio.setup(TOUCHINT, gpio.IN)
gpio.setup(PIR, gpio.IN)        
      
gpio.add_event_detect(TOUCHINT, gpio.RISING, callback=touch_debounce)    #touch interrupt
gpio.add_event_detect(PIR, gpio.BOTH, callback=motion_detected)  #motion detector interrupt

infrared_vals = np.full(100, np.nan)    
