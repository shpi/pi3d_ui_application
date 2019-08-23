installpath = '/home/pi/zero_thermostat_demo/'

TMDELAY = 30  #delay for changing backgrounds
INFRARED_TM = 5
SENSOR_TM = 10
ICAL_TM = 3600


show_airquality = 1 # show airquality over LED
starthttpserver = 1 #activate simple GET/POST server in python, be aware of  security issues
backlight_auto = 60  # timer for backlight auto off, 0 for always on
allowedips = list('192.168.1.31') #for check in server , not implemented so far

max_backlight = 31 # possible values  0 .. 31 


HYSTERESIS = 1.0  #  in degree
coolingrelay = 1 #1 #off
heatingrelay = 3 #3 #on relay3
shutterdown = 2 #1  #on
shutterup = 4 #4    # 4... buzzer, 5 d13, 6 hwb



icallink = 'muellkalender.ics'


slide = 0
subslide = None

#configurate your slides here

slides = ['thermostat','shutter','status','amperemeter','rrdgraph','ical','settings']

subslides = ['videostream','intercom','wifisetup','wifikeyboard']



