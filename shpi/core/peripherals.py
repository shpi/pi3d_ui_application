#!/usr/bin/env python
# -*- coding: utf-8 -*-
import RPi.GPIO as gpio
import sys
import numpy as np
import os
import time
import datetime
import struct
import pi3d
import threading
import logging
from pkg_resources import resource_filename

from .. import config
from ..core import i2c
from ..core import mqttclient

VALS = {  # various aliases for off and on
    '0': 0x00, 0: 0x00, 'OFF': 0x00,
    '1': 0xFF, 1: 0xFF, 'ON': 0xFF,
    'CLICK': 0x01,
}

COLOR_RED = 0x94
COLOR_GREEN = 0x95
COLOR_BLUE = 0x96
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
READ_RELAY1CURRENT = 0x14
READ_ATMEGA_TEMP = 0x0A
READ_ATMEGA_RAM = 0x0B
READ_RELAY1 = 0x0D
READ_RELAY2 = 0x0E
READ_RELAY3 = 0x0F
BACKLIGHT_LEVEL = 0x87
RELAY1 = 0x8D
RELAY2 = 0x8E
RELAY3 = 0x8F
D13 = 0x90
BUZZER = 0x92
VENT_PWM = 0x93

RELAYCHANNEL = [0x8D, 0x8E, 0x8F, 0x92, 0x90]

TOUCHADDR = 0x5c  # int 0 used to represent non-availability rather than False or None
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


def crc8(crc, n):
    """ CRC checksum algorithm """
    data = crc ^ n
    for _i in range(0, 8):
        if ((data & 0x80) != 0x00):
            data = (data << 1) & 0xFF
            data ^= 0x07
        else:
            data = (data << 1) & 0xFF
    return data


def i2crecover():
    try:
        addr = 3
        bus.read(1, 0x2A)
        bus.read(1, 0x2A)
        bus.read(1, 0x2A)
        bus.read(1, 0x2A)

        while([0x00] == bus.read(1, addr)):
            addr += 1
            if (addr > 119):
                addr = 3
            #logging.debug(str(i) + '.', end = "")
        time.sleep(0.01)
    except:
        time.sleep(0.01)


def touchloop():
    global xc, yc, lastx, lasty, touch_pressed, touch_file, lasttouch
    while True:
        event = touch_file.read(16)
        (_timestamp, _id, code, type, value) = struct.unpack('llHHI', event)
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
        time.sleep(0.05)


def alert(value=1):
    if value and (int)(time.time()) % 2 == 0:
        control_relay(4, 1)
        control_led([255, 0, 0])
        control_backlight_level(1)
        config.subslide = 'alert'
    else:
        control_relay(4, 0)
        control_led([0, 0, 0])
        control_backlight_level(eg_object.max_backlight)


def touched():
    return gpio.input(TOUCHINT)


def motion_detected(channel):
    global startmotion
    if gpio.input(channel):
        startmotion = time.time()
        logging.info('Motion detected!')
        eg_object.motion = True
        if config.START_MQTT_CLIENT:
            mqttclient.publish("motion", 'ON')
    else:
        logging.info('Motion time: ' +
                     str(round(time.time() - startmotion, 2)) + 's')
        eg_object.motion = False
        if config.START_MQTT_CLIENT:
            mqttclient.publish("motion", 'OFF')

    eg_object.lastmotion = time.time()


def get_touch():
    global xc, yc
    #global mouse, x_off, y_off
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
                        # logging.debug(x1,y1)
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
        if ADDR_32U4 != 0:
            clicksound()
        touch_pressed = True
        lastx = x
        lasty = y
    else:
        time.sleep(0.001)


def clicksound():
    global i2cerr, i2csucc
    try:
        crc = crc8(0, BUZZER)
        crc = crc8(crc, VALS['CLICK'])
        bus.write([BUZZER, VALS['CLICK'], crc], ADDR_32U4)
        crca = bus.read(1, ADDR_32U4)
        time.sleep(0.001)
        if ([crc] != crca):
            i2cerr += 1
        else:
            i2csucc += 1
    except:
        pass


def read_one_byte(addr_val, retries=0):  # utility function for brevity
    global i2cerr, i2csucc
    crc = 0
    try:
        crc = crc8(crc, addr_val)
        bus.write([addr_val], ADDR_32U4)
        b = bus.read(2, ADDR_32U4)
        crc = crc8(crc, b[0])
        time.sleep(0.001)
        if (crc == b[1]):
            i2csucc += 1
            return b[0]
        else:
            raise Exception("crc missmatch 0x{:02x}".format(addr_val))
    except Exception as e:  # potential inifinite loop - count repeats and break after n
        i2cerr += 1
        if retries < 10:
            time.sleep(0.1)
            return read_one_byte(addr_val, retries + 1)
        else:
            msg = "read_one_byte error: {}".format(e)
            # TODO return something on error and cope at receiving end
            logging.error(msg)


def read_two_bytes(addr_val, retries=0):  # utility function for brevity
    global i2cerr, i2csucc
    crc = 0
    try:
        crc = crc8(crc, addr_val)
        bus.write([addr_val], ADDR_32U4)
        b = bus.read(3, ADDR_32U4)
        crc = crc8(crc, b[0])
        crc = crc8(crc, b[1])
        time.sleep(0.001)
        if (crc == b[2]):
            i2csucc += 1
            return b[0] | (b[1] << 8)
        else:
            raise Exception("crc 2 missmatch 0x{:02x}".format(addr_val))
    except Exception as e:  # potential inifinite loop - count repeats and break after n
        i2cerr += 1
        if retries < 10:
            time.sleep(0.1)
            return read_two_bytes(addr_val, retries+1)
        else:
            msg = "read_two_bytes error: {}".format(e)
            logging.error(msg)


def control(attribute, value):
    """ finds and calls control function with name control_`attribute`
    if the last char of attribute is 0-9 then it's split from the name and passed as
    an argument to the function:
      relay2 => control_relay(2,...
    """
    if attribute[-1].isnumeric() and not attribute[-2].isnumeric():
        num = int(attribute[-1])
        attribute = attribute[:-1]
    else:
        num = -1
    func_name = 'control_{}'.format(attribute)
    if func_name in globals():
        if num == -1:
            return globals()[func_name](value)
        else:
            return globals()[func_name](num, value)
    else:
        return None  # TODO error logging


def write_32u4(addr, value, description, retries=0):
    """ generic function writing and checking crc8 on ADDR_32U4
    """
    global i2cerr, i2csucc
    try:
        crc = crc8(0, addr)
        crc = crc8(crc, value)
        bus.write([addr, value, crc], ADDR_32U4)
        crca = bus.read(1, ADDR_32U4)
        if ([crc] != crca):
            if crca == 0xFF:
                raise Exception(
                    "crc is 0xff, please check if u installed lates avr firmware, we changed LED control in atmega")
            else:
                raise Exception("crc8 mismatch")
        else:
            i2csucc += 1
    except Exception as e:
        if retries < 10:  # try recursively 10 times
            i2cerr += 1
            time.sleep(0.1)
            write_32u4(addr, value, description, retries+1)
        else:
            msg = "{} error: {}".format(description, e)
            logging.error(msg)  # TODO logging
            return (False, msg)
    return (True, value)


def control_relay(channel, value):
    if value not in VALS:
        return (False, "unknown VAL for value {}!".format(value))
    return write_32u4(RELAYCHANNEL[channel-1], VALS[value], "relay{}".format(channel))


def control_vent_pwm(value):
    value = int(value)  # variable int value
    if not (-1 < value < 256):
        return (False, "value outside 0..255")
    return write_32u4(VENT_PWM, value, "vent_pwm")


def control_backlight_level(value):
    file_path = resource_filename("shpi", "bin/backlight")
    try:
        value = int(value)
        assert -1 < value <= config.MAX_BACKLIGHT, "value outside permitted range"
        # needs sudo because of timing
        os.popen('sudo chrt --rr 99 {} {}'.format(file_path, value))
        return write_32u4(BACKLIGHT_LEVEL, value, "backlight_level")
    except Exception as e:
        return (False, "backlight_level error: {}".format(e))


def control_led_color(channel, rgbvalue):
    return write_32u4(channel, int(rgbvalue), "led_color")


def control_led(rgbvalues):
    if type(rgbvalues) not in (list, tuple):
        rgbvalues = rgbvalues.split(",")
    if len(rgbvalues) == 3:
        # splitted because of i2c master  clockstretching problems
        control_led_color(COLOR_RED, rgbvalues[0])
        control_led_color(COLOR_GREEN, rgbvalues[1])
        control_led_color(COLOR_BLUE, rgbvalues[2])
        eg_object.led = rgbvalues
        return (True, rgbvalues)
    else:
        return (False, "error, wrong rgbvalues for control_led")


def control_alert(value):
    value = int(value)
    eg_object.alert = value  # TODO error catching?
    return(True, value)


def control_buzzer(value):
    return control_relay(4, value)


def control_slide(value):
    value = int(value)
    if not (-1 < value < len(config.slides)):
        return (False, "value outside number of slides")
    eg_object.slide = value
    return (True, value)


def control_d13(value):
    return control_relay(5, value)


def control_max_backlight(value):
    value = int(value)
    if not (-1 < value < 32):
        return (False, "value outside 0 to 31")
    eg_object.max_backlight = value
    return (True, value)


def control_set_temp(value):
    value = float(value)
    if not (0.0 < value < 50.0):
        return (False, "value outside 0.0 to 50.0")
    eg_object.set_temp = value
    return (True, value)


def heating():
    if (eg_object.act_temp + config.HYSTERESIS) < eg_object.set_temp + eg_object.tempoffset:
        control_relay(config.HEATINGRELAY, 1)
    elif (eg_object.act_temp - config.HYSTERESIS) > eg_object.set_temp + eg_object.tempoffset:
        control_relay(config.HEATINGRELAY, 0)


def cooling():
    if (eg_object.act_temp + config.HYSTERESIS) < eg_object.set_temp + eg_object.tempoffset:
        control_relay(config.COOLINGRELAY, 1)
    elif (eg_object.act_temp - config.HYSTERESIS) > eg_object.set_temp + eg_object.tempoffset:
        control_relay(config.COOLINGRELAY, 0)


def coolingheating():
    if eg_object.set_temp + eg_object.tempoffset - config.HYSTERESIS < eg_object.act_temp < eg_object.set_temp + eg_object.tempoffset + config.HYSTERESIS:
        control_relay(config.HEATINGRELAY, 0)
    else:
        control_relay(config.HEATINGRELAY, 1)


def get_infrared():
    global infrared_vals, lasttouch
    # take values only if there is no motion or user touch interaction
    if eg_object.lastmotion < (time.time() - 5) and (gpio.input(TOUCHINT) == 0 and ADDR_MLX):
        # try:
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

        infrared_vals[:-1] = infrared_vals[1:]

        # compensate own self heating
        if (eg_object.mlxamb > eg_object.mlxobj):
            infrared_vals[-1] = (eg_object.mlxobj
                                 - (eg_object.mlxamb - eg_object.mlxobj) / 6)
        else:
            infrared_vals[-1] = eg_object.mlxobj

        eg_object.act_temp = np.nanmedian(infrared_vals)

        try:
            if (infrared_vals[-1] - 1) > infrared_vals[-2]:
                eg_object.lastmotion = time.time()
                #logging.error('waked screen because of deltaT increase of MLX')
        except Exception as e:
            logging.error('infrared error:{}'.format(e))


def get_status():
    try:
        eg_object.i2cerrorrate = int(100 * i2cerr / i2csucc)
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
                eg_object.tempoffsetstr = '+' + str(eg_object.tempoffset)
            elif eg_object.tempoffset < 0:
                eg_object.tempoffsetstr = str(eg_object.tempoffset)
            else:
                eg_object.tempoffsetstr = ' '
        else:
            eg_object.tempoffset = 0
            eg_object.tempoffsetstr = ' '

        if ADDR_32U4 != 0:
            time.sleep(0.05)
            eg_object.backlight_level = read_one_byte(READ_BACKLIGHT_LEVEL)
            eg_object.vent_pwm = read_one_byte(READ_VENT_PWM)
            time.sleep(0.05)
            eg_object.relay1 = 1 if read_one_byte(READ_RELAY1) == 255 else 0
            eg_object.relay2 = 1 if read_one_byte(READ_RELAY2) == 255 else 0
            time.sleep(0.05)
            eg_object.relay3 = 1 if read_one_byte(READ_RELAY3) == 255 else 0
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

            bus.read(1, ADDR_32U4)

            if (crc != b[3]):
                logging.error('crc8 error read rgb led')
            else:
                eg_object.led_red = b[0]
                eg_object.led_green = b[1]
                eg_object.led_blue = b[2]
                eg_object.led = [eg_object.led_red,
                                 eg_object.led_green, eg_object.led_blue]
    except Exception as e:
        logging.error(e)


def get_sensor_uhrzeit():
    eg_object.uhrzeit = time.strftime("%H:%M")


def get_sensor_gputemp():
    eg_object.gputemp = float(
        os.popen("vcgencmd measure_temp").readline()[5:-3])


def get_sensor_cputemp():
    eg_object.cputemp = float(os.popen(
        "cat /sys/class/thermal/thermal_zone0/temp").readline()) / 1000


def get_sensor_sht_temp_humidity():
    if (gpio.input(TOUCHINT) == 0):
        if ADDR_SHT != 0:
            try:
                time.sleep(0.001)
                # clockstretching disabled , softreset: 0x30A2 or general call: 0x0006
                bus.write([0x24, 0x00], ADDR_SHT)
                time.sleep(0.05)
                data = bus.read(6, ADDR_SHT)
                eg_object.sht_temp = float(
                    ((data[0] * 256.0 + data[1]) * 175) / 65535.0 - 45)
                eg_object.humidity = 100 * (data[3] * 256 + data[4]) / 65535.0
            except Exception as e:
                logging.error('error SHT: {}'.format(e))


def get_sensor_lightlevel():
    if (gpio.input(TOUCHINT) == 0):
        if ADDR_BH1750 != 0:
            try:
                time.sleep(0.001)
                # 0x20 highres 1 lux prec.,  0x21 highres2 0.5lux prec., 0x23 4 lux prec. fast!
                data = bus.rdwr([0x23], 2, ADDR_BH1750)
                eg_object.lightlevel = (float)(
                    (data[1] + (256 * data[0])) / 1.2)
            except Exception as e:
                logging.error('error BH1750: {}'.format(e))


def get_sensor_bmp_temp_pressure():
    global dig_T, dig_P
    if (gpio.input(TOUCHINT) == 0):
        if ADDR_BMP != 0:
            try:
                time.sleep(0.001)
                bus.write([0xF4, 0x27], ADDR_BMP)
                bus.write([0xF5, 0xA0], ADDR_BMP)
                data = bus.rdwr([0xF7], 8, ADDR_BMP)
                adc_p = ((data[0] * 65536) + (data[1] * 256) +
                         (data[2] & 0xF0)) / 16
                adc_t = ((data[3] * 65536) + (data[4] * 256) +
                         (data[5] & 0xF0)) / 16
                _adc_h = data[6] * 256 + data[7]
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
                    var1 = (dig_P[2] * var1 * var1 / 524288.0
                            + dig_P[1] * var1) / 524288.0
                    var1 = (1.0 + var1 / 32768.0) * (dig_P[0])
                    p = 1048576.0 - adc_p
                    p = (p - (var2 / 4096.0)) * 6250.0 / var1
                    var1 = (dig_P[8]) * p * p / 2147483648.0
                    var2 = p * (dig_P[7]) / 32768.0
                    eg_object.pressure = (
                        p + (var1 + var2 + (dig_P[6])) / 16.0) / 100
            except Exception as e:
                logging.error('error BMP: {}'.format(e))


def get_sensor_32u4():
    if (gpio.input(TOUCHINT) == 0):
        if ADDR_32U4 != 0:
            time.sleep(0.07)
            factor = 5000.0 / 1024.0 / 185.0
            eg_object.relay1current = factor * \
                (read_two_bytes(READ_RELAY1CURRENT) - 2)
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


def get_sensor_aht10_temp_humidity():
    if (gpio.input(TOUCHINT) == 0):
        if ADDR_AHT10 != 0:
            try:
                time.sleep(0.001)
                bus.write([0xAC, 0x00, 0x00], ADDR_AHT10)
                time.sleep(0.4)
                temp = bus.read(6, ADDR_AHT10)
                eg_object.humidity = (temp[1] << 12 | temp[2] << 4 | (
                    temp[3] & 0xf0) >> 4) * 100.0 / (1 << 20)
                eg_object.sht_temp = (
                    (temp[3] & 0xf) << 16 | temp[4] << 8 | temp[5]) * 200.0 / (1 << 20) - 50
            except Exception as e:
                logging.error('error aht10: {}'.format(e))


def get_sensors():  # readout all sensor values, system, and atmega vars
    get_sensor_uhrzeit()
    get_sensor_gputemp()
    get_sensor_cputemp()
    get_sensor_sht_temp_humidity()
    get_sensor_lightlevel()
    get_sensor_bmp_temp_pressure()
    get_sensor_32u4()
    get_sensor_aht10_temp_humidity()


class EgClass(object):
    if ADDR_32U4 != 0:
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
        relay1current = 0.0

    # if ADDR_MLX:
    mlxamb = 0.0
    mlxobj = 0.0
    relay0 = 0
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
    relay1 = 0
    relay2 = 0
    relay3 = 0
    lastmotion = time.time()
    max_backlight = config.MAX_BACKLIGHT
    usertext = ''
    usertextshow = '|'
    alert = 0
    led = [led_red, led_green, led_blue]


""" End of definitions section
"""
# checks if touchdriver is running
os_touchdriver = os.popen('pgrep -f touchdriver.py -c').readline()

if int(os_touchdriver) > 1:
    try:
        touch_file = open("/dev/input/event1", "rb")
    except:
        touch_file = open("/dev/input/event0", "rb")

startmotion = time.time()
i2cerr, i2csucc = 1, 1
xc, yc = 0, 0
lastx, lasty = 0, 0
touch_pressed = 0
lasttouch = 0

bus = i2c.I2C(2)
# bus.set_timeout(3)

try:
    bus.read(1, TOUCHADDR)
    # interrupt configuration i2c
    bus.write([0x6e, 0b00001110], TOUCHADDR)
    bus.write([0x70, 0b00000000], TOUCHADDR)
except:
    logging.error('Error: no touchscreen found')
    TOUCHADDR = False

# check for atmega  -> future: lite or std SHPI
try:
    time.sleep(0.001)
    bus.read(1, ADDR_32U4)
except:
    ADDR_32U4 = 0
    logging.warning('Hint: No ATmega found, seems to be a SHPI.zero lite?')

# check for SHT3x
try:
    time.sleep(0.001)
    bus.write([0x01], ADDR_SHT)
except:
    ADDR_SHT = 0
    logging.warning('Hint: No SHT found')

try:
    time.sleep(0.001)
    bus.write([0xA8, 0x00, 0x00], ADDR_AHT10)
    bus.write([0xAC, 0x00, 0x00], ADDR_AHT10)
    time.sleep(0.3)
    bus.write([0xE1, 0x08, 0x00], ADDR_AHT10)
    response = bus.read(1, ADDR_AHT10)
    if (response[0] & 0x68 == 0x08):
        logging.warning('Hint: AHT10 calibrated')
    else:
        logging.warning('Hint: AHT10 error occured')
    # time.sleep(0.5)
except:
    ADDR_AHT10 = 0
    logging.warning('Hint: no AHT10 found')

# check for light sensor BH1750
try:
    time.sleep(0.001)
    bus.write([0x01], ADDR_BH1750)  # power on BH1750
except:
    logging.warning('Hint: No BH1750')
    ADDR_BH1750 = 0

# check for MLX90615
try:
    time.sleep(0.001)
    bus.rdwr([0x26], 2, ADDR_MLX)
except:
    ADDR_MLX = False
    logging.warning('Hint: No MLX90615 found')

# correction values for BMP280
try:
    time.sleep(0.001)
    b1 = bytes(bus.rdwr([0x88], 24, ADDR_BMP))
    dig_T = struct.unpack_from('<Hhh', b1, 0)
    dig_P = struct.unpack_from('<Hhhhhhhhh', b1, 6)
except:
    logging.warning('Hint: No BMP280 found')
    ADDR_BMP = 0

i2crecover()

eg_object = EgClass()

gpio.setmode(gpio.BCM)
gpio.setwarnings(False)
gpio.setup(TOUCHINT, gpio.IN, pull_up_down=gpio.PUD_DOWN)
gpio.setup(PIR, gpio.IN, pull_up_down=gpio.PUD_DOWN)

if int(os_touchdriver) < 2:
    gpio.add_event_detect(TOUCHINT, gpio.RISING,
                          callback=touch_debounce)  # touch interrupt
else:
    #start_new_thread(touchloop, ())
    t = threading.Thread(target=touchloop)
    t.start()

# motion detector interrupt
gpio.add_event_detect(PIR, gpio.BOTH, callback=motion_detected)

infrared_vals = np.full(100, np.nan)
