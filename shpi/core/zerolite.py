import RPi.GPIO as gpio

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
