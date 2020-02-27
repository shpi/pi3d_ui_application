installpath = '/home/pi/zero_main_application/'

DEMO = True  # shows demo slides

TMDELAY = 200  # delay for changing backgrounds
INFRARED_TM = 3
SENSOR_TM = 10
ICAL_TM = 3600  # update calenderslide every 3600 seconds
SLIDE_PARALLAX = True
SLIDE_SHADOW = False  # shadow effect while manually sliding
SHOW_AIRQUALITY = True  # show airquality over LED
# activate simple GET/POST server in python, be aware of  security issues
START_HTTP_SERVER = True
HTTP_PORT = 9000
SHUTTERTIMER = 30  # timer for auto deactivation of shutter relais
START_MQTT_CLIENT = True
MQTT_USER = ''
MQTT_PW = ''
MQTT_SERVER = "mqtt.eclipse.org"
MQTT_PORT = 1883
MQTT_PATH = "shpi"
MQTT_QOS = 1

MOTION_THRESHOLD = 4  # threshold in seconds of movement

BACKLIGHT_AUTO = 60  # timer for backlight auto off, 0 for always on
# for check in server , not implemented so far
ALLOWEDDIPS = list('192.168.1.31')


MAX_BACKLIGHT = 31  # possible values  0 .. 31
MIN_BACKLIGHT = 1

HYSTERESIS = 0.5  # in degree
set_temp = 23
COOLINGRELAY = 0   #off
HEATINGRELAY = 1  #on relay 1
SHUTTERDOWN = 2  #relay 2
SHUTTERUP = 3  # relay 3   #  4... buzzer, 5 d13, 6 hwb
LIGHTRELAY = 0 #off
VENTRELAY = 0 #off
MIN_HUMIDITY_THRESHOLD = 0
MAX_HUMIDITY_THRESHOLD = 0
AIR_QUALITY_THRESHOLD = 0

ICALLINK = 'muellkalender.ics'  # also http possible

OWMKEY = '20f7aab0a600927a8486b220200ee694'
OWMLANGUAGE = 'de'
OWMCITY = 'Berlin, DE'

WEEKDAYS = ['Montag', 'Dienstag', 'Mittwoch',
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

# configure your slides here
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


if DEMO:
    slides.append('demo_floorplan')
    slides.append('demo_remote_button')


subslides = ['videostream', 'intercom', 'wifisetup', 'wifikeyboard', 'alert']
