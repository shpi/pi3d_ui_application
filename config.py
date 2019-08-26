installpath = '/home/pi/zero_main_application/'

demo = 1  #shows demo slides

TMDELAY = 30  #delay for changing backgrounds
INFRARED_TM = 5
SENSOR_TM = 10
ICAL_TM = 3600  #update calenderslide every 3600 seconds


show_airquality = 1 # show airquality over LED
starthttpserver = 1 #activate simple GET/POST server in python, be aware of  security issues
HTTP_PORT = 9000

startmqttclient = 1
MQTT_USER = ''
MQTT_PW = ''
MQTT_SERVER = "mqtt.eclipse.org" 
MQTT_PORT = 1883
MQTT_PATH = "shpi"
MQTT_QOS = 1

backlight_auto = 60  # timer for backlight auto off, 0 for always on
allowedips = list('192.168.1.31') #for check in server , not implemented so far


max_backlight = 31 # possible values  0 .. 31 


HYSTERESIS = 1.0  #  in degree
coolingrelay = 1 #1 #off
heatingrelay = 3 #3 #on relay3
shutterdown = 2 #1  #on
shutterup = 4 #4    # 4... buzzer, 5 d13, 6 hwb



icallink = 'muellkalender.ics' #also http possible


slide = 0
subslide = None

#configurate your slides here

slides = ['thermostat','shutter','status','amperemeter','rrdgraph','ical','settings']

if demo: slides.append('demo_remote_button')


subslides = ['videostream','intercom','wifisetup','wifikeyboard','alert']



