installpath = '/home/pi/zero_main_application/'

demo = 1  #shows demo slides

TMDELAY = 30  #delay for changing backgrounds
INFRARED_TM = 5
SENSOR_TM = 10
ICAL_TM = 3600  #update calenderslide every 3600 seconds


show_airquality = 0 # show airquality over LED
starthttpserver = 1 #activate simple GET/POST server in python, be aware of  security issues
HTTP_PORT = 9000
shuttertimer = 30 # timer for auto deactivation of shutter relais
startmqttclient = 0
MQTT_USER = ''
MQTT_PW = ''
MQTT_SERVER = "mqtt.eclipse.org" 
MQTT_PORT = 1883
MQTT_PATH = "shpi"
MQTT_QOS = 1

backlight_auto = 60  # timer for backlight auto off, 0 for always on
allowedips = list('192.168.1.31') #for check in server , not implemented so far


max_backlight = 31 # possible values  0 .. 31 


HYSTERESIS = 0.5  #  in degree

coolingrelay = 0 #1 #off
heatingrelay = 1 #3 #on relay3
shutterdown = 2 #1  #on
shutterup = 3 #4    # 4... buzzer, 5 d13, 6 hwb



icallink = 'muellkalender.ics' #also http possible

owmkey = '20f7aab0a600927a8486b220200ee694'
owmlanguage = 'de'
owmcity = 'Berlin, DE'


slide = 0
subslide = None

#configurate your slides here

slides = ['thermostat','weather','status','shutter','livegraph','amperemeter','rrdgraph','ical','settings']

if demo:
  slides.append('demo_floorplan') 
  slides.append('demo_remote_button')


subslides = ['videostream','intercom','wifisetup','wifikeyboard','alert']



