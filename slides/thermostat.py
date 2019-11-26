#!/usr/bin/env python
# -*- coding: utf-8 -*-

import core.peripherals as peripherals
import core.graphics as graphics
import config
import os
import sys
import pi3d

sys.path.insert(1, os.path.join(sys.path[0], '..'))


try:
    unichr
except NameError:
    unichr = chr


text = pi3d.PointText(graphics.pointFont, graphics.CAMERA,
                      max_chars=220, point_size=128)
temp_block = pi3d.TextBlock(-350, 50, 0.1, 0.0, 15, data_obj=peripherals.eg_object, attr="act_temp",
                            text_format=unichr(0xE021) + u"{:2.1f}°C", size=0.99, spacing="F", space=0.05, colour=(1.0, 1.0, 1.0, 1.0))
text.add_text_block(temp_block)

if config.heatingrelay or config.coolingrelay:
    set_temp_block = pi3d.TextBlock(-340, -30, 0.1, 0.0, 15, data_obj=peripherals.eg_object, text_format=unichr(0xE005) + u" {:2.1f}°C", attr="set_temp",
                                    size=0.5, spacing="F", space=0.05, colour=(1.0, 1.0, 1.0, 1.0))
    text.add_text_block(set_temp_block)
    offset_temp_block = pi3d.TextBlock(-70, -30, 0.1, 0.0, 15, data_obj=peripherals.eg_object, text_format=u"{:s}", attr="tempoffsetstr",
                                       size=0.5, spacing="F", space=0.05, colour=(1.0, 1.0, 1.0, 1.0))
    text.add_text_block(offset_temp_block)

    if peripherals.eg_object.tempoffset > 0:
        offset_temp_block.colouring.set_colour([1, 0, 0])
    elif peripherals.eg_object.tempoffset < 0:
        offset_temp_block.colouring.set_colour([0, 0, 1])
    else:
        offset_temp_block.colouring.set_colour([1, 1, 1])

    increaseTemp = pi3d.TextBlock(300, 150, 0.1, 180.0, 1, text_format=unichr(
        0xE000), size=0.99, spacing="C", space=0.6, colour=(1, 0, 0, 0.8))
    text.add_text_block(increaseTemp)
    decreaseTemp = pi3d.TextBlock(300, -50, 0.1, 0.0, 1, text_format=unichr(
        0xE000), size=0.99, spacing="C", space=0.6, colour=(0, 0, 1, 0.8))
    text.add_text_block(decreaseTemp)
    cloud = pi3d.TextBlock(30, -30, 0.1, 0.0, 1, text_format=unichr(0xE002),
                           size=0.5, spacing="C", space=0.6, colour=(1, 1, 1, 0.9))
    text.add_text_block(cloud)

if hasattr(peripherals.eg_object, 'pressure'):
    barometer = pi3d.TextBlock(80, -25, 0.1, 0.0, 2, text_format=unichr(
        0xE00B), size=0.6, spacing="F", space=0.05, colour=(1.0, 1.0, 1.0, 0.9))
    text.add_text_block(barometer)
    baroneedle = pi3d.Triangle(camera=graphics.CAMERA, corners=(
        (-3, 0, 0), (0, 15, 0), (3, 0, 0)), x=barometer.x+32, y=barometer.y - 12, z=0.1)
    baroneedle.set_shader(graphics.MATSH)

newtxt = pi3d.TextBlock(270, -180, 0.1, 0.0, 15, text_format=unichr(0xE001),
                        size=0.99, spacing="F", space=0.05, colour=(1.0, 1.0, 1.0, 1.0))
text.add_text_block(newtxt)
motiondetection = pi3d.TextBlock(290, -175, 0.1, 0.0, 15, text_format=unichr(
    0xE01C), size=0.79, spacing="F", space=0.05, colour=(1.0, 1.0, 1.0, 1.0))
text.add_text_block(motiondetection)

if config.heatingrelay:
    newtxt = pi3d.TextBlock(145, -180, 0.1, 0.0, 15, text_format=unichr(
        0xE001), size=0.99, spacing="F", space=0.05, colour=(1.0, 1.0, 1.0, 1.0))
    text.add_text_block(newtxt)
    heating = pi3d.TextBlock(172, -180, 0.1, 0.0, 15, text_format=unichr(
        0xE004), size=0.79, spacing="F", space=0.05, colour=(1.0, 1.0, 1.0, 1.0))
    text.add_text_block(heating)

if config.coolingrelay:
    newtxt = pi3d.TextBlock(20, -180, 0.1, 0.0, 15, text_format=unichr(0xE001),
                            size=0.99, spacing="F", space=0.05, colour=(1.0, 1.0, 1.0, 1.0))
    text.add_text_block(newtxt)
    cooling = pi3d.TextBlock(42, -182, 0.1, 0.0, 15, text_format=unichr(
        0xE029), size=0.79, spacing="F", space=0.05, colour=(1.0, 1.0, 1.0, 1.0))
    text.add_text_block(cooling)

if 'videostream' in config.subslides:
    newtxt = pi3d.TextBlock(-400, -180, 0.1, 0.0, 15, text_format=unichr(
        0xE001), size=0.99, spacing="F", space=0.05, colour=(1.0, 1.0, 1.0, 1.0))
    text.add_text_block(newtxt)
    newtxt = pi3d.TextBlock(-385, -180, 0.1, 0.0, 15, text_format=unichr(
        0xE02F), size=0.79, spacing="F", space=0.05, colour=(1.0, 1.0, 1.0, 1.0))
    text.add_text_block(newtxt)

if 'intercom' in config.subslides:
    newtxt = pi3d.TextBlock(-300, -180, 0.1, 0.0, 15, text_format=unichr(
        0xE001), size=0.99, spacing="F", space=0.05, colour=(1.0, 1.0, 1.0, 1.0))
    text.add_text_block(newtxt)
    newtxt = pi3d.TextBlock(-275, -180, 0.1, 0.0, 15, text_format=unichr(
        0xE031), size=0.79, spacing="F", space=0.05, colour=(1.0, 1.0, 1.0, 1.0))
    text.add_text_block(newtxt)

controls_alpha = 1


def inloop(textchange=False, activity=False, offset=0):

    global controls_alpha

    if offset != 0:
        offset = graphics.slider_change(text.text, offset)
        if offset == 0:
            textchange = True


    if textchange:

        if peripherals.eg_object.tempoffset > 0:
            offset_temp_block.colouring.set_colour([1, 0, 0])
        elif peripherals.eg_object.tempoffset < 0:
            offset_temp_block.colouring.set_colour([0, 0, 1])
        else:
            offset_temp_block.colouring.set_colour([1, 1, 1])

        red = (0.01 * (peripherals.eg_object.a4/4))
        if (red > 1):
            red = 1

        green = (0.01 * (120 - peripherals.eg_object.a4/4))
        if green < 0:
            green = 0
        if green > 1:
            green = 1

        cloud.colouring.set_colour([red, green, 0, 1.0])

        if config.coolingrelay:
            if getattr(peripherals.eg_object, 'relais' + (str)(config.coolingrelay)):
                cooling.colouring.set_colour([0, 0, 1])
            else:
                cooling.colouring.set_colour([1, 1, 1])

        if config.heatingrelay:
            if getattr(peripherals.eg_object, 'relais' + (str)(config.heatingrelay)):
                heating.colouring.set_colour([1, 1, 0])
            else:
                heating.colouring.set_colour([1, 1, 1])

        if hasattr(peripherals.eg_object, 'pressure'):
            normalizedpressure = (peripherals.eg_object.pressure - 950)
            if normalizedpressure < 0:
                normalizedpressure = 0
            if normalizedpressure > 100:
                normalizedpressure = 100
            green = 0.02 * (normalizedpressure)
            if green > 1:
                green = 1
            red = 0.02 * (100 - normalizedpressure)
            if red > 1:
                red = 1
            barometer.colouring.set_colour([red, green, 0, 1.0])
            baroneedle.set_material([red, green, 0])
            baroneedle.rotateToZ(100 - (normalizedpressure*2))
        text.regen()

    if hasattr(peripherals.eg_object, 'pressure') and offset == 0:
        baroneedle.draw()

    if (peripherals.eg_object.motion):
        motiondetection.colouring.set_colour([1, 0, 0])
    else:
        motiondetection.colouring.set_colour([1, 1, 1])

    if peripherals.touch_pressed:
        peripherals.touch_pressed = False

        if config.heatingrelay or config.coolingrelay:

            if peripherals.clicked(increaseTemp.x, increaseTemp.y):
                controls_alpha = 1
                peripherals.eg_object.set_temp += 0.5
                set_temp_block.colouring.set_colour([1, 0, 0])
                text.regen()
            if peripherals.clicked(decreaseTemp.x, decreaseTemp.y):
                controls_alpha = 1
                peripherals.eg_object.set_temp -= 0.5
                set_temp_block.colouring.set_colour([0, 0, 1])
                text.regen()

        if peripherals.clicked(-330, -180):
            config.subslide = 'videostream'

            try:
                os.popen('killall omxplayer.bin')
            except:
                pass

            os.popen(
                'omxplayer --threshold 0.5  --display 4 rtsp://username:pass@192.168.1.5:554/mpeg4cif --win "0 0 800 450"')
            # loading time depends on keyframes in stream, only h264 recommended!

        if 'intercom' in config.subslides and peripherals.clicked(-230, -180):
            config.subslide = 'intercom'

            try:
                os.popen('killall omxplayer.bin')
                os.popen('killall raspivid')
            except:
                pass

            os.popen('gpio -g write 27 1')  # deactivate amplifier
            os.popen('i2cset -y 2 0x2A 0x93 210')  # deactivate vent
            os.popen("amixer -c 1 set 'PCM' 0%")  # deactivate soundcard out
            os.popen("amixer -c 1 set 'Mic' 0%")  # enable mic
            config.iip = '192.168.1.22'
            config.iuser = 'pi'
            config.ipw = 'raspberry'
            os.popen('sshpass -p \'raspberry\' ssh -o StrictHostKeyChecking=no  pi@' + config.iip +
                     ' "raspivid  -t 0 -w 640 -h 480 -g 10 -ih -fps 25 -l -p \'640,0,160,120\' -o  tcp://0.0.0.0:5001"')
            os.popen('sshpass -p \'raspberry\' ssh -o StrictHostKeyChecking=no  pi@' + config.iip +
                     ' "arecord -D plughw:1,0 -r 12000 -f S16_LE -c1 -B 300 -t wav | nc -l 5003"')

            os.popen(
                'raspivid  -t 0 -w 640 -h 480 -g 10  -ih -fps 25 -hf  -vf -l -p \'640,0,160,120\' -o  tcp://0.0.0.0:5002')
            os.popen('sleep 2 && nc ' + config.iip +
                     ' 5001 | ./videoplayer 0 0 640 480')
            os.popen('sleep 2 && nc ' + config.iip +
                     '  5003 | { dd bs=60K count=1 iflag=fullblock of=/dev/null; aplay -c 1 --device=plughw:1,0 -B 0 -f S16_LE -c1 -r 12000 -t wav; }')
            os.popen(
                'arecord -D plughw:1,0 -r 12000 -f S16_LE -c1 -B 300 -t wav | nc -l 5004')

            os.popen('sshpass -p \'raspberry\' ssh -o StrictHostKeyChecking=no  pi@' +
                     config.iip + ' "nc 192.168.1.33 5002 | ./videoplayer 0 0 640 480"')
            os.popen('sshpass -p \'raspberry\' ssh -o StrictHostKeyChecking=no  pi@' + config.iip +
                     ' "nc 192.168.1.33 5004 | { dd bs=60K count=1 iflag=fullblock of=/dev/null; aplay -c 1 --device=plughw:1,0 -B 0 -f S16_LE -c1 -r 12000 -t wav; }"')

    # nc 192.168.1.33 5003 | { dd bs=60K count=1 iflag=fullblock of=/dev/null; aplay -c 1 --device=plughw:1,0 -B 0 -f S16_LE -c1 -r 12000 -t wav; }
    # arecord -D plughw:1,0 -r 12000 -f S16_LE -c1 -B 300 -t wav | nc -l 5003

    if controls_alpha > 0.3:
        activity = True
        controls_alpha -= 0.01
    if config.heatingrelay or config.coolingrelay:
        increaseTemp.colouring.set_colour(alpha=controls_alpha)
        decreaseTemp.colouring.set_colour(alpha=controls_alpha)
        set_temp_block.colouring.set_colour(alpha=controls_alpha)
        offset_temp_block.colouring.set_colour(alpha=controls_alpha)

    if controls_alpha < 0.3:

        if config.heatingrelay or config.coolingrealy:
            set_temp_block.colouring.set_colour([1, 1, 1])


    text.draw()

    return activity, offset
