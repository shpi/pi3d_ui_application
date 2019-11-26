installpath = '/home/pi/zero_main_application/'

demo = 1  # shows demo slides

TMDELAY = 200  # delay for changing backgrounds
INFRARED_TM = 5
SENSOR_TM = 10
ICAL_TM = 3600  # update calenderslide every 3600 seconds

slideshadow = 0  # shadow effect while manually sliding
show_airquality = 1  # show airquality over LED
# activate simple GET/POST server in python, be aware of  security issues
starthttpserver = 1
HTTP_PORT = 9000
shuttertimer = 30  # timer for auto deactivation of shutter relais
startmqttclient = 0
MQTT_USER = ''
MQTT_PW = ''
MQTT_SERVER = "mqtt.eclipse.org"
MQTT_PORT = 1883
MQTT_PATH = "shpi"
MQTT_QOS = 1

motionthreshold = 4  # threshold in seconds of movement

backlight_auto = 60  # timer for backlight auto off, 0 for always on
# for check in server , not implemented so far
allowedips = list('192.168.1.31')


max_backlight = 31  # possible values  0 .. 31
min_backlight = 1

HYSTERESIS = 0.5  # in degree
set_temp = 23
coolingrelay = 0  # 1 #off
heatingrelay = 1  # 3 #on relay3
shutterdown = 2  # 1  #on
shutterup = 3  # 4    # 4... buzzer, 5 d13, 6 hwb
lightrelay = 0
ventrelay = 0
minhumiditythreshold = 0
maxhumiditythreshold = 0
airqualitythreshold = 0

icallink = 'muellkalender.ics'  # also http possible

owmkey = '20f7aab0a600927a8486b220200ee694'
owmlanguage = 'de'
owmcity = 'Berlin, DE'

weekdays = ['Montag', 'Dienstag', 'Mittwoch',
            'Donnerstag', 'Freitag', 'Samstag', 'Sonntag']

# day / week temperature curves, only save delta t from setting temperature (to keep  user interface easy)

daytempcurve = 0
daytempdelta = [-2,  # 0:00  - 1:00
                -2,  # 1:00  - 2:00
                -2,  # 2:00  - 3:00
                -2,  # 3:00  - 4:00
                -2,  # 4:00  - 5:00
                -1,  # 5:00  - 6:00
                -1,  # 6:00  - 7:00
                -1,  # 7:00  - 8:00
                0,  # 8:00  - 9:00
                0,  # 9:00  - 10:00
                0,  # 10:00 - 11:00
                0,  # 11:00 - 12:00
                0,  # 12:00 - 13:00
                0,  # 13:00
                0,  # 14:00
                1,  # 15:00
                1,  # 16:00
                1,  # 17:00
                1,  # 18:00
                1,  # 19:00
                0,  # 20:00
                0,  # 21:00
                -1,  # 22:00
                -1]  # 23:00

weektempcurve = 0
weektempdelta = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # monday
                 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # tuesday
                 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # wednesday
                 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # thursday
                 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # friday
                 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # saturday
                 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]  # sunday

slide = 0
subslide = None

# configurate your slides here
autoslidetm = 10
autoslides = []
slides = ['overview','thermostat', 'weather', 'ical2', 'status', 'shutter',
          'livegraph', 'amperemeter', 'rrdgraph', 'settings']
autoslideints = []

for autoslide in autoslides:
    i = 0
    for sslide in slides:
        if sslide == autoslide:
            autoslideints.append(i)
        i += 1


if demo:
    slides.append('demo_floorplan')
    slides.append('demo_remote_button')


subslides = ['videostream', 'intercom', 'wifisetup', 'wifikeyboard', 'alert']
