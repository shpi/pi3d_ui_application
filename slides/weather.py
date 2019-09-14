#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pi3d
import sys,os
import time
import datetime

import numpy as np
import math

try:
 import pyowm
except ImportError:
    exit("Please run: (sudo) pip3 install pyowm")


sys.path.insert(1, os.path.join(sys.path[0], '..'))

import config
import core.graphics as graphics
import core.peripherals as peripherals

import os.path



threehours = time.time()

grapharea = pi3d.Sprite(camera=graphics.CAMERA,w=780,h=100,z=3.0, x = 0, y = -180)
grapharea.set_shader(graphics.MATSH)
grapharea.set_material((1.0, 1.0, 1.0))
grapharea.set_alpha(0.3)
grapharea2 = pi3d.Sprite(camera=graphics.CAMERA,w=780,h=350,z=3.0, x = 0, y = 55)
grapharea2.set_shader(graphics.MATSH)
grapharea2.set_material((0, 0, 0))
grapharea2.set_alpha(0.7)

def init():
 global seplines,degwind,weathericon,text,line,baroneedle,windneedle,linemin,linemax,acttemp
 text = pi3d.PointText(graphics.pointFont, graphics.CAMERA, max_chars=700, point_size=128) 


 owm = pyowm.OWM(API_key=config.owmkey,language=config.owmlanguage) 
 place = owm.weather_at_place(config.owmcity)
 weather = place.get_weather()


 if config.owmlanguage == 'de':
  weekdays = ['Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag', 'Samstag', 'Sonntag']
 else:
   weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
 
 
 if  not os.path.exists('sprites/'+ weather.get_weather_icon_name() + '.png'):

  import urllib.request
  urllib.request.urlretrieve("http://openweathermap.org/img/wn/" + weather.get_weather_icon_name() + "@2x.png", "sprites/" + weather.get_weather_icon_name() + ".png")

 weathericon = pi3d.ImageSprite('sprites/' + weather.get_weather_icon_name() + '.png',shader=graphics.SHADER,camera=graphics.CAMERA,w=150,h=150,z=2,x=-220)
 city = pi3d.TextBlock(-390, 180, 0.1, 0.0, 150, text_format= place.get_location().get_name() , size=0.7, spacing="F", space=0.05,colour=(1.0, 1.0, 1.0,1.0))
 text.add_text_block(city)

 city = pi3d.TextBlock(-380, 80, 0.1, 0.0, 30, text_format= weather.get_detailed_status() , size=0.4, spacing="F", space=0.05,colour=(1.0, 1.0, 1.0,1.0))
 text.add_text_block(city)



 # acttemp = pi3d.TextBlock(-280, 0, 0.1, 0.0, 10, text_format= str(weather.get_temperature(unit='celsius')['temp']) + '°C'  ,  size=0.5, spacing="F",space=0.05,colour=(1.0, 1.0, 1.0,1.0))
 #text.add_text_block(acttemp)
 acttemp = pi3d.FixedString(config.installpath + 'fonts/opensans.ttf', str(weather.get_temperature(unit='celsius')['temp']) + '°C'   , font_size=42, shadow_radius=1,justify='L', color= (255,255,255,255),camera=graphics.CAMERA, shader=graphics.SHADER, f_type='SMOOTH')
 acttemp.sprite.position(-210, -50, 1)
 sunriset = weather.get_sunrise_time(timeformat='date') + datetime.timedelta(hours=2)
 sunsett = weather.get_sunset_time(timeformat='date') + datetime.timedelta(hours=2)
 sunset = pi3d.TextBlock(50, 100, 0.1, 0.0, 20, text_format= chr(0xE041) +  " %s:%s" % (sunriset.hour, sunriset.minute) + ' ' + chr(0xE042) +  " %s:%s" % (sunsett.hour, sunsett.minute)  ,  size=0.3, spacing="F", 
                                                                                                              space=0.05,colour=(1.0, 1.0, 1.0,1.0))
 text.add_text_block(sunset)



 barometer = pi3d.TextBlock(50, -50, 0.1, 0.0, 10, text_format= chr(0xE00B) + ' ' + str(weather.get_pressure()['press']) + ' hPa' , size=0.3, spacing="F", space=0.05,colour=(1.0, 1.0, 1.0,1.0))
 text.add_text_block(barometer)
 baroneedle = pi3d.Triangle(camera=graphics.CAMERA, corners=((-2,0,0),(0,7,0),(2,0,0)), x=barometer.x+16, y=barometer.y - 6, z=0.1)
 baroneedle.set_shader(graphics.MATSH)
 normalizedpressure = (weather.get_pressure()['press'] - 950)
 if normalizedpressure < 0: normalizedpressure = 0
 if normalizedpressure >  100: normalizedpressure = 100
 green = 0.02 * (normalizedpressure)
 if green > 1: green = 1
 red = 0.02 * (100 - normalizedpressure)
 if red > 1: red = 1
 barometer.colouring.set_colour([red, green , 0, 1.0])
 baroneedle.set_material([red,green,0])
 baroneedle.rotateToZ(100 - (normalizedpressure*2))


 humidity = pi3d.TextBlock(50, 0, 0.1, 0.0, 10, text_format= chr(0xE003) + ' ' + str(weather.get_humidity()) + '%' , size=0.3, spacing="F", space=0.05, colour=(1.0, 1.0, 1.0, 1.0))
 text.add_text_block(humidity)




 if 'speed' in weather.get_wind():
   wind = pi3d.TextBlock(50, 50, 0.1, 0.0, 10, text_format= chr(0xE040) + ' ' + str(weather.get_wind()['speed']) + 'm/s' , size=0.3, spacing="F", space=0.05, colour=(1.0, 1.0, 1.0, 1.0))
   text.add_text_block(wind)


 if 'deg' in weather.get_wind():
   degwind = True
   windneedle = pi3d.Triangle(camera=graphics.CAMERA, corners=((-3,0,0),(0,15,0),(3,0,0)), x=wind.x+180, y=wind.y, z=0.1)
   windneedle.set_shader(graphics.MATSH)
   windneedle.set_material([1,1,1])
   windneedle.rotateToZ(weather.get_wind()['deg'])
 else:
   degwind = False


 fc = owm.three_hours_forecast(config.owmcity)
 f = fc.get_forecast()

 step = 780 / (len(f))
 actualy = -400 + step
 temp_max = []
 temp_min = []
 temp = []
 seplines = []
 icons = []

 maxdaytemp = -100
 mindaytemp = 100

 for weather in f:

      if  not os.path.exists('sprites/'+ weather.get_weather_icon_name() + '.png'):

        import urllib.request
        urllib.request.urlretrieve("http://openweathermap.org/img/wn/" + weather.get_weather_icon_name() + "@2x.png", "sprites/" + weather.get_weather_icon_name() + ".png")

      icons.append(pi3d.ImageSprite('sprites/' + weather.get_weather_icon_name() + '.png',shader=graphics.SHADER,camera=graphics.CAMERA,w=20,h=20,z=1,x = actualy, y= -220))
        


      if weather.get_reference_time('iso')[11:16] == '00:00':
          line = pi3d.Lines(vertices=[[actualy,-50,2],[actualy,50,2]], line_width=1,y=-180, strip=True)
          line.set_shader(graphics.MATSH)
          line.set_material((0,0,0))
          line.set_alpha(0.9)
          seplines.append(line)
      #if weather.get_reference_time('iso')[11:16] == '12:00':
          day = weather.get_reference_time(timeformat='date').weekday()
          if actualy < 300:
           city = pi3d.TextBlock(actualy+5, -100, 0.1, 0.0, 30, text_format= weekdays[day] , size=0.3, spacing="F", space=0.05,colour=(1.0, 1.0, 1.0,1.0))
           text.add_text_block(city)
          if actualy > -300:
           city = pi3d.TextBlock(actualy-6*step, -150, 0.1, 0.0, 30, text_format= str(round(maxdaytemp,1)) + '°C' , size=0.25, spacing="F", space=0.05,colour=(1.0, 0.0, 0.0,1.0))
           text.add_text_block(city)
           city = pi3d.TextBlock(actualy-6*step, -210, 0.1, 0.0, 30, text_format= str(round(mindaytemp,1)) + '°C' , size=0.25, spacing="F", space=0.05,colour=(0.0, 0.0, 1.0,1.0))
           text.add_text_block(city)


          maxdaytemp = -100
          mindaytemp = 100





      if '3h' in weather.get_snow():
          line = pi3d.Lines(vertices=[[actualy,-50,2],[actualy,(-50+weather.get_snow()['3h']*30),2]], line_width=3,y=-180, strip=True)
          line.set_shader(graphics.MATSH)
          line.set_material((0.5,0.5,1))
          line.set_alpha(1)
          seplines.append(line)

      if '3h' in weather.get_rain():
          line = pi3d.Lines(vertices=[[actualy,-50,2],[actualy,(-50+weather.get_rain()['3h']*30),2]], line_width=3,y=-180, strip=True)
          line.set_shader(graphics.MATSH)
          line.set_material((0,0,1))
          line.set_alpha(1)
          seplines.append(line)

      temperatures = weather.get_temperature(unit='celsius')
      if temperatures['temp_max'] > maxdaytemp: maxdaytemp = temperatures['temp_max']
      if temperatures['temp_min'] < mindaytemp: mindaytemp = temperatures['temp_min']


      temp_max.append([actualy,temperatures['temp_max']*3,2])
      temp_min.append([actualy,temperatures['temp_min']*3,2])
      temp.append([actualy,temperatures['temp']*3,2])
      actualy +=step




 lastvalue =  0

 line = pi3d.Lines(vertices=temp, line_width=2,y=-220, strip=True)
 line.set_shader(graphics.MATSH)
 line.set_material((0,0,0))
 line.set_alpha(0.9)

 linemin = pi3d.Lines(vertices=temp_min, line_width=1,y=-220, strip=True)
 linemin.set_shader(graphics.MATSH)
 linemin.set_material((0,0,1))
 linemin.set_alpha(0.9)

 linemax = pi3d.Lines(vertices=temp_max, line_width=1,y=-220, strip=True)
 linemax.set_shader(graphics.MATSH)
 linemax.set_material((1,0,0))
 linemax.set_alpha(0.9)

init()


def inloop(textchange = False,activity = False, offset = 0):
     global seplines,degwind,threehours,weathericon,text,line,baroneedle,windneedle,linemin,linemax,acttemp


     if (time.time() > threehours) and offset == 0:
        init()  
        threehours = time.time() + (60*60*3)  

     grapharea2.draw()
     grapharea.draw()
     text.draw()

   

     if offset != 0:
         #graphics.slider_change(city.sprite, offset)

         offset = graphics.slider_change(text.text, offset)
              
     else:
     
       weathericon.draw()
       acttemp.draw()
       baroneedle.draw()
       line.draw()
       linemin.draw()
       linemax.draw()   
       if degwind: windneedle.draw()
       for subline in seplines: subline.draw()
       #for icon in icons: icon.draw()




     return activity,offset




















