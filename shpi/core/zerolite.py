import RPi.GPIO as gpio
import spidev
import os
import time

class ZeroLite():
    def __init__(self):
        # default GPIOs for Lite - do these need to be settable via arguments?
        self.FAN_PIN = 18
        self.PIR = 10
        self.RELAY = [27, 11, 1]

        gpio.setmode(gpio.BCM)
        gpio.setup(self.FAN_PIN, gpio.OUT)
        self.p = gpio.PWM(self.FAN_PIN, 50)  # channel=18 frequency=50Hz
        self.p.start(0)
        gpio.setup(self.RELAY, gpio.OUT) # can take array argument to set several
        self.fan_factor = 100.0 / 255.0 # TODO might this need to vary?
        self.spi = spidev.SpiDev()


    def set_fan(self, value=0.0):
        value = max(0.0, min(100.0, value * self.fan_factor))
        self.p.ChangeDutyCycle(value)
        return (True, value)


    def set_relay(self, relay, value):
        value = value & 1 # could get 0x00, 0x01 or 0xFF
        gpio.output(self.RELAY[relay], value)
        return (True, value) 


    def get_relay(self, relay):
        return gpio.input(self.RELAY[relay])


    def set_buzzer(self, value=0):
        # TODO if this needs reading and writing from i2c bus maybe keep in peripherals
        return (True, value)


    def control_led(self, rgbvalues):
        os.popen('gpio -g mode 10 alt0') #TODO will this always be 10
        self.spi.open(0, 0)
        self.spi.mode = 0b11
        grb = [rgbvalues[1], rgbvalues[0], rgbvalues[2]]
        tx = [0b11000000 if ((i >> j) &1) == 0 else 0b11111000
                for i in grb
                    for j in range(7,-1,-1)]
        time.sleep(0.2) # this sleep seems essential
        self.spi.xfer(tx, int(8 / 1.25e-6))
        self.spi.close()
        os.popen('gpio -g mode 10 input') # don't know if this is needed TODO 10?
        gpio.setup(10, gpio.IN, pull_up_down=gpio.PUD_DOWN) #is this duplicating above? TODO 10?
        time.sleep(0.01)
