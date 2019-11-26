#!/usr/bin/env python
# -*- coding: utf-8 -*-
import config
import RPi.GPIO as gpio
import sys
import numpy as np
import os
import time
import struct
import pi3d
import core.i2c as i2c

try:
    import mqttclient
except:
    import core.mqttclient as mqttclient


sys.path.insert(1, os.path.join(sys.path[0], '..'))


# checks if touchdriver is running
os_touchdriver = os.popen('pgrep -f touchdriver.py -c').readline()

if int(os_touchdriver) > 1:
    print('os touch driver active')
    try:
        from _thread import start_new_thread
    except:
        from thread import start_new_thread
    touch_file = open("/dev/input/event1", "rb")


startmotion, i2cerr, i2csucc, xc, yc, lastx, lasty, touch_pressed, lasttouch = time.time(), 0, 0, 0, 0, 0, 0, 0, 0


def crc8(crc, n):

    data = crc ^ n
    for i in range(0, 8):
        if ((data & 0x80) != 0x00):
            data = (data << 1) & 0xFF
            data ^= 0x07
        else:
            data = (data << 1) & 0xFF
    return data


def i2crecover():
    try:
        addr = 3
        while([0x00] == bus.read(1, addr)):
            addr += 1
            if (addr > 119):
                addr = 3
            #print(str(i) + '.', end = "")
        time.sleep(0.01)
    except:
        time.sleep(0.1)
        pass


def touchloop():
    global xc, yc, lastx, lasty, touch_pressed, touch_file, lasttouch
    while True:
        event = touch_file.read(16)
        (timestamp, id, code, type, value) = struct.unpack('llHHI', event)
        if code == 3 and type == 0:
            xc = value - 400
        if code == 3 and type == 1:
            yc = -(value - 240)
        if code == 1 and type == 330:
            if value:
                eg_object.lastmotion = time.time()  # wake screen up on touch
                lasttouch = time.time()
                touch_pressed = True
                lastx = xc
                lasty = yc
            else:
                lastx = 0
        #   touch_pressed = False


VALS = {  # various aliases for off and on
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
ADDR_AHT10 = 0x38
ADDR_MLX = 0x5B
ADDR_BH1750 = 0x23
PIR = 18
# single wire backlight control needs almost realtime -> moved to atmega  (not on prototypes!)
BACKLIGHT = 19
TOUCHINT = 26


bus = i2c.I2C(2)
#bus.set_timeout(3)


try:
    bus.read(1, TOUCHADDR)
    # interrupt configuration i2c
    bus.write([0x6e, 0b00001110], TOUCHADDR)
    bus.write([0x70, 0b00000000], TOUCHADDR)
except:
    print('no touchscreen found')
    TOUCHADDR = False


# check for atmega  -> future: lite or std SHPI
try:
    time.sleep(0.001)
    bus.read(1, ADDR_32U4)

except:
    ADDR_32U4 = False
    print('no ATmega found, seems to be a SHPI.zero lite?')


# check for SHT3x
try:
    time.sleep(0.001)
    bus.write([0x01], ADDR_SHT)
except:
    ADDR_SHT = False
    print('no SHT found')


try:
    time.sleep(0.001)
    bus.write([0xA8, 0x00, 0x00], ADDR_AHT10)
    bus.write([0xAC, 0x00, 0x00], ADDR_AHT10)
    time.sleep(0.3)
    bus.write([0xE1, 0x08, 0x00], ADDR_AHT10)
    response = bus.read(1, ADDR_AHT10)
    if (response[0] & 0x68 == 0x08):
        print('AHT10 calibrated')
    else:
        print('AHT10 error occured')
    # time.sleep(0.5)

except:
    ADDR_AHT10 = False
    print('no AHT10 found')

# check for light sensor BH1750
try:
    time.sleep(0.001)
    bus.write([0x01], ADDR_BH1750)  # power on BH1750
except:
    print('no BH1750')
    ADDR_BH1750 = False


# check for MLX90615
try:
    print('check mlx')
    time.sleep(0.001)
    bus.rdwr([0x26], 2, ADDR_MLX)
except:
    ADDR_MLX = False
    print('no MLX90615 found')

# correction values for BMP280
try:
    print('check bmp')
    time.sleep(0.001)
    b1 = bytes(bus.rdwr([0x88], 24, ADDR_BMP))
    dig_T = struct.unpack_from('<Hhh', b1, 0)
    dig_P = struct.unpack_from('<Hhhhhhhhh', b1, 6)



except:
    print('no bmp280')
    ADDR_BMP = 0


i2crecover()


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

    # if ADDR_MLX:
    mlxamb = 0.0
    mlxobj = 0.0
    relais0 = 0
    # if ADDR_BMP:
    bmp280_temp = 0.0
    pressure = 0.0

    # if ADDR_BH1750:
    lightlevel = 0.0

    # if ADDR_SHT:
    sht_temp = 0.0
    humidity = 0.0

    # if ADDR_AHT10:
    sht_temp = 0.0
    humidity = 0.0

    motion = False
    set_temp = config.set_temp
    backlight_level = 0
    i2cerrorrate = 0
    gputemp = 0
    cputemp = 0
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
    tempoffset = 0
    tempoffsetstr = " "
    uhrzeit = "00:00"
    relais1 = 0
    relais2 = 0
    relais3 = 0
    lastmotion = time.time()
    max_backlight = config.max_backlight
    usertext = ''
    usertextshow = '|'
    alert = 0
    led = [led_red, led_green, led_blue]


eg_object = EgClass()



def alert(value=1):
    if value and (int)(time.time()) % 2 == 0:
        controlrelays(4, 1)
        controlled([255, 0, 0])
        controlbacklight(1)
        config.subslide = 'alert'
    else:
        controlrelays(4, 0)
        controlled([0, 0, 0])
        controlbacklight(eg_object.max_backlight)


def touched():
    return gpio.input(TOUCHINT)


def motion_detected(channel):
    global startmotion
    if gpio.input(channel):
        startmotion = time.time()
        print('motion detected')
        eg_object.motion = True
        if config.startmqttclient:
            mqttclient.publish("motion", 'ON')
    else:

        print('motion time: ' + str(time.time() - startmotion))
        eg_object.motion = False
        if config.startmqttclient:
            mqttclient.publish("motion", 'OFF')

    eg_object.lastmotion = time.time()


def get_touch():
    global xc, yc, os_touchdriver, mouse, x_off, y_off
    if int(os_touchdriver) > 1:
        return xc, yc

    elif TOUCHADDR:
        if (gpio.input(TOUCHINT)):
            try:
                time.sleep(0.001)
                data = bus.rdwr([0x40], 8, TOUCHADDR)
                x1 = 400 - (data[0] | (data[4] << 8))
                y1 = (data[1] | (data[5] << 8)) - 240

                if ((-401 < x1 < 401) & (-241 < y1 < 241)):
                    if ((-80 < (xc-x1) < 80) & (-80 < (yc-y1) < 80)):  # catch bounches
                        xc = x1
                        yc = y1
                        # print(x1,y1)

                        return xc, yc  # compensate position to match with PI3D
                    else:
                        xc = x1
                        yc = y1
                        time.sleep(0.01)
                        return get_touch()
                else:
                    return xc, yc

            except:
                time.sleep(0.05)
                return xc, yc
        else:
            return xc, yc
    else:
        return xc, yc


def clicked(x, y):
    global lastx, lasty

    if ((x - 50) < lastx < (x + 50)) and ((y - 50) < lasty < (y + 50)):
        return True
    else:
        return False


def touch_debounce(channel):
    global lastx, lasty, touch_pressed, lasttouch

    x, y = get_touch()
    lasttouch = time.time()
    if (channel == TOUCHINT):
        eg_object.lastmotion = time.time()  # wake screen up on touch
        if ADDR_32U4:
            clicksound()
        touch_pressed = True
        lastx = x
        lasty = y
    else:
        time.sleep(0.001)


def clicksound():
    global i2cerr,i2csucc
    try:
        crc = crc8(0, BUZZER)
        crc = crc8(crc, VALS['CLICK'])
        bus.write([BUZZER, VALS['CLICK'], crc], ADDR_32U4)
        crca = bus.read(1, ADDR_32U4)
        time.sleep(0.001)
        if ([crc] != crca):
            i2cerr +=1
        else: i2csucc +=1
    except:
        pass

def controlrelays(channel, value, retries=0):
    global i2cerr,i2csucc
    try:
        crc = crc8(0, RELAYCHANNEL[channel-1])
        crc = crc8(crc, VALS[value])
        bus.write([RELAYCHANNEL[channel-1], VALS[value], crc], ADDR_32U4)
        crca = bus.read(1, ADDR_32U4)

        if ([crc] != crca):
            i2cerr +=1
            if retries > 10: 
              print('crc8 error: set relays')
              i2crecover()
              controlrelays(channel,value)
            else:
              time.sleep(0.1)
              controlrelays(channel, value,retries+1)
        else: 
            i2csucc += 1 
   
    except Exception as e: 
        if retries < 10:
            i2cerr += 1
            time.sleep(0.1)
            controlrelays(channel, value, retries + 1)
        else: 
            print('i2c blocked setting channels: {}'.format(e))
            i2crecover()
            controlrelays(channel,value)

def read_one_byte(addr_val,retries=0):  # utility function for brevity
    global i2cerr,i2csucc
    crc = 0
    try:
        crc = crc8(crc, addr_val)
        bus.write([addr_val], ADDR_32U4)
        b = bus.read(2, ADDR_32U4)
        crc = crc8(crc, b[0])
        time.sleep(0.001)
        if (crc == b[1]):
            i2csucc +=1
            return b[0]
        else:
          i2cerr +=1
          if retries < 10:
            time.sleep(0.1)
            return read_one_byte(addr_val,retries+1)
          else:
            print('crc missmatch ' + ' 0x{:02x}'.format(addr_val))
            i2crecover()
            return read_one_byte(addr_val)
    except Exception as e:  # potential inifinite loop - count repeats and break after n
       i2cerr +=1
       if retries < 10:
           time.sleep(0.1)
           return read_one_byte(addr_val,retries+1)
       else:
        print('i2c blocked ' + '0x{:02x}'.format(addr_val))
        i2crecover()
        return read_one_byte(addr_val)


def read_two_bytes(addr_val,retries=0):  # utility function for brevity
    global i2cerr,i2csucc
    crc = 0
    try:
        crc = crc8(crc, addr_val)
        bus.write([addr_val], ADDR_32U4)
        b = bus.read(3, ADDR_32U4)
        crc = crc8(crc, b[0])
        crc = crc8(crc, b[1])
        time.sleep(0.001)
        if (crc == b[2]):
            i2csucc +=1
            return b[0] | (b[1] << 8)
        else:
          i2cerr += 1
          if retries < 10:
            time.sleep(0.1)
            return read_two_bytes(addr_val,retries+1)
          else:
            print('crc 2 missmatch 0x{:02x}'.format(addr_val))
            i2crecover()
            return read_two_bytes(addr_val)

    except Exception as e:  # potential inifinite loop - count repeats and break after n
      i2cerr +=1
      if retries < 10:
       time.sleep(0.1)
       return  read_two_bytes(addr_val,retries+1)
      else:
        print('i2c bus blocked 0x{:02x}'.format(addr_val))
        i2crecover()
        return read_two_bytes(addr_val)


def controlvent(value,retries=0):
    global i2cerr,i2csucc
    try:
        value = int(value)  # variable int value
        assert -1 < value < 256, 'value outside 0..255'
        crc = crc8(0, VENT_PWM)
        crc = crc8(crc, value)
        bus.write([VENT_PWM, value, crc], ADDR_32U4)
        crca = bus.read(1, ADDR_32U4)
        if ([crc] != crca):
            i2cerr +=1
            if retries < 10:
             time.sleep(0.1)
             controlvent(value,retries+1)
            else:
             print('control vent crc missmatch')
             i2crecover()
             controlvent(value)
        else: 
             i2csucc +=1
    except Exception as e:
        i2cerr +=1
        if retries < 10:
           time.sleep(0.1)
           controlvent(value,retries+1)
        else:
           print('control vent i2c error')
           i2crecover()
           conrolvent(value)


def controlbacklight(value,retries=0):
    global i2cerr,i2csucc
    os.popen('sudo chrt --rr 99 ' + config.installpath +
             'bin/backlight {}'.format(value))  # needs sudo because of timing
    try:
        crc = crc8(0, BACKLIGHT_LEVEL)
        crc = crc8(crc, value)
        bus.write([BACKLIGHT_LEVEL, value, crc], ADDR_32U4)
        crca = bus.read(1, ADDR_32U4)

        if ([crc] != crca):
            i2cerr +=1
            if retries < 10:
               time.sleep(0.1)
               controlbacklight(value,retries+1)
            else:
              print('control backlight crc missmatch, retry')
              i2crecover()
              controlbacklight(value)
        else: i2csucc +=1
    except:
        i2cerr +=1
        if retries < 10:
          time.sleep(0.1)
          controlbacklight(value,retries+1)
        else:
          print('control backlight crc error')
          i2crecover()
          controlbacklight(value)
          


def controlled(rgbvalues, retries=0):
    global i2cerr,i2csucc

    if len(rgbvalues) == 3: 
      if eg_object.led != rgbvalues:

        crc = crc8(0, 0x8C)
        rgb = [0x8C]
        for value in rgbvalues:
            value = int(value)  # variable int value
            assert -1 < value < 256, 'value outside 0..255'
            rgb.append(value)
            crc = crc8(crc, value)
        rgb.append(crc)
        try: 
            bus.write(rgb, ADDR_32U4)
            crca = False
            while (crca == False):
              try:
                   crca = bus.read(1, ADDR_32U4)
              except: pass
            if ([crc] != crca):
                i2cerr +=1
                if retries < 10:
                   time.sleep(0.1)
                   controlled(rgbvalues,retries+1)
                else:
                 print('control rgb led crc8 missmatch, retry')
                 i2crecover()
                 controlled(rgbvalues) 
            else:
              i2csucc +=1
              eg_object.led = rgbvalues
        except Exception as e:  # potential inifinite loop - count repeats and break after n
            i2cerr +=1
            if retries < 10:
                time.sleep(0.1)
                controlled(rgbvalues,retries+1)
            else:
             print('i2c blocked setting led: {}'.format(e))
             i2crecover()
             controlled(rgbvalues)
            
    else:
        print('error, wrong rgbvalues for controlled')

        # cooling & heating function


def heating():
    if (eg_object.act_temp + config.HYSTERESIS) < eg_object.set_temp + eg_object.tempoffset:
        controlrelays(config.heatingrelay, 1)

    elif (eg_object.act_temp - config.HYSTERESIS) > eg_object.set_temp + eg_object.tempoffset:
        controlrelays(config.heatingrelay, 0)


def cooling():
    if (eg_object.act_temp + config.HYSTERESIS) < eg_object.set_temp + eg_object.tempoffset:
        controlrelays(config.coolingrelay, 1)
    elif (eg_object.act_temp - config.HYSTERESIS) > eg_object.set_temp + eg_object.tempoffset:
        controlrelays(config.coolingrelay, 0)


def coolingheating():
    if eg_object.set_temp + eg_object.tempoffset - config.HYSTERESIS < eg_object.act_temp < eg_object.set_temp + eg_object.tempoffset + config.HYSTERESIS:
        controlrelays(config.heatingrelay, 0)
    else:
        controlrelays(config.heatingrelay, 1)


def get_infrared():
    global infrared_vals

    if (gpio.input(TOUCHINT) == 0 and ADDR_MLX):
        try:
            time.sleep(0.1)
            b = bus.rdwr([0x26], 2, ADDR_MLX)
            value = float(((b[0] | b[1] << 8) * 0.02) - 273.15)
            if (-50 < value < 80):
                eg_object.mlxamb = value
            time.sleep(0.001)
            b = bus.rdwr([0x27], 2, ADDR_MLX)
            value = float(((b[0] | b[1] << 8) * 0.02) - 273.15)
            if (-50 < value < 80):
                eg_object.mlxobj = value
            time.sleep(0.1)

            # compensate own self heating
            if (eg_object.mlxamb > eg_object.mlxobj):
                infrared_vals[-1] = eg_object.mlxobj - \
                    ((eg_object.mlxamb - eg_object.mlxobj) / 6)
            else:
                infrared_vals[-1] = eg_object.mlxobj

            infrared_vals[:-1] = infrared_vals[1:]
            eg_object.act_temp = np.nanmedian(infrared_vals)

        except Exception as e:
            print('error MLX:' + str(e))


def get_status():
    global i2csucc, i2cerr
    try:
        eg_object.i2cerrorrate = int(100 / (i2csucc / i2cerr))
        eg_object.useddisk = os.popen(
            "df | grep root  | awk '{print $5}'").readline().strip()
        eg_object.load = float(os.getloadavg()[0])
        s = os.statvfs('/')
        eg_object.freespace = float((s.f_bavail * s.f_frsize) / 1024 / 1024)
        eg_object.wifistrength = (os.popen(
            "/sbin/iwconfig wlan0 | grep 'Signal level' | awk '{print $4}' | cut -d= -f2 | cut -d/ -f1;").readline()).strip()
        eg_object.ipaddress = os.popen(
            "ip addr show wlan0 | grep 'inet ' | head -1 | awk '{print $2}' | cut -d/ -f1;").readline().strip()
        eg_object.ssid = (os.popen(
            "/sbin/iwconfig wlan0 | grep \"SSID:\" | awk \"{print $4}\" | cut -d'\"' -f2").readline()).strip()

        if config.daytempcurve:
            eg_object.tempoffset = config.daytempdelta[int(
                time.strftime("%H"))]
            if eg_object.tempoffset > 0:
                eg_object.tempoffsetstr = '+' + str(eg_object.tempoffset)
            elif eg_object.tempoffset < 0:
                eg_object.tempoffsetstr = str(eg_object.tempoffset)
            else:
                eg_object.tempoffsetstr = ' '

        elif config.weektempcurve:
            eg_object.tempoffset = config.weektempdelta[datetime.date.today(
            ).weekday()][int(time.strftime('%H'))]
            if eg_object.tempoffset > 0:
                eg_object.tempoffsetstr = '+' + str( eg_object.tempoffset)
            elif eg_object.tempoffset < 0:
                eg_object.tempoffsetstr = str(eg_object.tempoffset)
            else:
                eg_object.tempoffsetstr = ' '

        else:
            eg_object.tempoffset = 0
            eg_object.tempoffsetstr = ' '

        if ADDR_32U4:

            time.sleep(0.05)
            eg_object.backlight_level = read_one_byte(READ_BACKLIGHT_LEVEL)
            eg_object.vent_pwm = read_one_byte(READ_VENT_PWM)
            time.sleep(0.05)
            eg_object.relais1 = 1 if read_one_byte(READ_RELAIS1) == 255 else 0
            eg_object.relais2 = 1 if read_one_byte(READ_RELAIS2) == 255 else 0
            time.sleep(0.05)
            eg_object.relais3 = 1 if read_one_byte(READ_RELAIS3) == 255 else 0
            eg_object.d13 = 1 if read_one_byte(READ_D13) == 255 else 0
            time.sleep(0.05)
            eg_object.hwb = 1 if read_one_byte(READ_HWB) == 255 else 0
            eg_object.buzzer = 1 if read_one_byte(READ_BUZZER) == 255 else 0
            eg_object.vent_rpm = read_two_bytes(READ_VENT_RPM)
            eg_object.atmega_ram = read_two_bytes(READ_ATMEGA_RAM)

            crc = crc8(0, 0x0C)
            bus.write([0x0C], ADDR_32U4)
            b = bus.read(4, ADDR_32U4)
            crc = crc8(crc, b[0])
            crc = crc8(crc, b[1])
            crc = crc8(crc, b[2])

            bus.read(1,ADDR_32U4)

            if (crc != b[3]):
                print('crc8 error read rgb led')
            else:
                eg_object.led_red = b[0]
                eg_object.led_green = b[1]
                eg_object.led_blue = b[2]
                eg_object.led = led = [eg_object.led_red,
                                       eg_object.led_green, eg_object.led_blue]

    except Exception as e:
        print(e)


def get_sensors():  # readout all sensor values, system, and atmega vars
    global infrared_vals, dig_T, dig_P
    if (gpio.input(TOUCHINT) == 0):

        eg_object.uhrzeit = time.strftime("%H:%M")
        eg_object.gputemp = float(
            os.popen("vcgencmd measure_temp").readline()[5:-3])
        eg_object.cputemp = float(
            os.popen("cat /sys/class/thermal/thermal_zone0/temp").readline()) / 1000

        if ADDR_SHT:
            try:
                time.sleep(0.001)
                # clockstretching disabled , softreset: 0x30A2 or general call: 0x0006
                bus.write([0x24, 0x00], ADDR_SHT)
                time.sleep(0.05)
                data = bus.read(6, ADDR_SHT)
                eg_object.sht_temp = float(
                    ((((data[0] * 256.0) + data[1]) * 175) / 65535.0) - 45)
                eg_object.humidity = 100 * (data[3] * 256 + data[4]) / 65535.0
            except Exception as e:
                print('error SHT:' + str(e))

        if ADDR_BH1750:
            try:
                time.sleep(0.001)
                # 0x20 highres 1 lux prec.,  0x21 highres2 0.5lux prec., 0x23 4 lux prec. fast!
                data = bus.rdwr([0x23], 2, ADDR_BH1750)
                eg_object.lightlevel = (float)(
                    (data[1] + (256 * data[0])) / 1.2)
            except Exception as e:
                print('error BH1750:' + str(e))

        if ADDR_BMP:
            try:
                time.sleep(0.001)
                bus.write([0xF4, 0x27], ADDR_BMP)
                bus.write([0xF5, 0xA0], ADDR_BMP)
                data = bus.rdwr([0xF7], 8, ADDR_BMP)
                adc_p = ((data[0] * 65536) + (data[1] * 256) +
                         (data[2] & 0xF0)) / 16
                adc_t = ((data[3] * 65536) + (data[4] * 256) +
                         (data[5] & 0xF0)) / 16
                adc_h = data[6] * 256 + data[7]
                var1 = ((adc_t) / 16384.0 - (dig_T[0]) / 1024.0) * (dig_T[1])
                var2 = (((adc_t) / 131072.0 - (dig_T[0]) / 8192.0) * (
                    (adc_t)/131072.0 - (dig_T[0])/8192.0)) * (dig_T[2])
                t_fine = (var1 + var2)
                value = float((var1 + var2) / 5120.0)
                if (-50 < value < 80):
                    eg_object.bmp280_temp = value
                    var1 = (t_fine / 2.0) - 64000.0
                    var2 = var1 * var1 * (dig_P[5]) / 32768.0
                    var2 = var2 + var1 * (dig_P[4]) * 2.0
                    var2 = (var2 / 4.0) + ((dig_P[3]) * 65536.0)
                    var1 = ((dig_P[2]) * var1 * var1 /
                            524288.0 + (dig_P[1]) * var1) / 524288.0
                    var1 = (1.0 + var1 / 32768.0) * (dig_P[0])
                    p = 1048576.0 - adc_p
                    p = (p - (var2 / 4096.0)) * 6250.0 / var1
                    var1 = (dig_P[8]) * p * p / 2147483648.0
                    var2 = p * (dig_P[7]) / 32768.0
                    eg_object.pressure = (
                        p + (var1 + var2 + (dig_P[6])) / 16.0) / 100
            except Exception as e:
                print('error BMP:' + str(e))

        if ADDR_32U4:

            time.sleep(0.07)
            eg_object.relais1current = (((5000/1024) *
                                         (read_two_bytes(READ_RELAIS1CURRENT) - 2)) / 185)
            eg_object.atmega_temp = read_two_bytes(
                READ_ATMEGA_TEMP) * 0.558 - 142.5
            time.sleep(0.01)
            eg_object.atmega_volt = read_two_bytes(READ_ATMEGA_VOLT)
            eg_object.a0 = read_two_bytes(READ_A0)
            time.sleep(0.05)
            eg_object.a1 = read_two_bytes(READ_A1)
            eg_object.a2 = read_two_bytes(READ_A2)
            eg_object.a3 = read_two_bytes(READ_A3)
            time.sleep(0.05)
            eg_object.a4 = read_two_bytes(READ_A4)
            eg_object.a5 = read_two_bytes(0x05)
            eg_object.a7 = read_two_bytes(0x06)

        if ADDR_AHT10:

            try:
                time.sleep(0.001)
                bus.write([0xAC, 0x00, 0x00], ADDR_AHT10)
                time.sleep(0.4)
                temp = bus.read(6, ADDR_AHT10)
                eg_object.humidity = (temp[1] << 12 | temp[2] << 4 | (
                    temp[3] & 0xf0) >> 4) * 100.0 / (1 << 20)
                eg_object.sht_temp = (
                    (temp[3] & 0xf) << 16 | temp[4] << 8 | temp[5]) * 200.0 / (1 << 20) - 50
            except:
                print('error aht10')


gpio.setmode(gpio.BCM)
gpio.setwarnings(False)
gpio.setup(TOUCHINT, gpio.IN, pull_up_down=gpio.PUD_DOWN)
gpio.setup(PIR, gpio.IN, pull_up_down=gpio.PUD_DOWN)

if int(os_touchdriver) < 2:
    gpio.add_event_detect(TOUCHINT, gpio.RISING,
                          callback=touch_debounce)  # touch interrupt
else:
    start_new_thread(touchloop, ())


# motion detector interrupt
gpio.add_event_detect(PIR, gpio.BOTH, callback=motion_detected)

infrared_vals = np.full(100, np.nan)
