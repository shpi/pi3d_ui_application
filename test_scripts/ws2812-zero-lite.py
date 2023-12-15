#!/usr/bin/python
import numpy
import spidev
import RPi.GPIO as gpio
import os, time 


def write2812(data,spi = spidev.SpiDev()):
    #gpio.setup(10,gpio.OUT)
    #gpio.output(10,gpio.HIGH)
    
    os.popen('gpio -g mode 10 alt0')
    spi.open(0,0)
    spi.mode = 0b11
    d=numpy.array(data).ravel()
    tx=numpy.zeros(len(d)*8, dtype=numpy.uint8)
    for ibit in range(8):
        tx[7-ibit::8]=((d>>ibit)&1)*0x78 + 0x80
    spi.xfer(tx.tolist(), int(8/1.25e-6))
    spi.close()
    


gpio.setmode(gpio.BCM)    
gpio.setwarnings(False)
gpio.setup(10, gpio.IN,pull_up_down=gpio.PUD_DOWN)        
print(gpio.input(10))

write2812([0,0,0])

gpio.setup(10, gpio.IN,pull_up_down=gpio.PUD_DOWN)        
print(gpio.input(10))

