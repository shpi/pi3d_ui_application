#!/usr/bin/python
from __future__ import absolute_import, division, print_function, unicode_literals


import smbus
#import numpy as np

# measure Relais 1 0x8D -> 0xFF to switch on
bus = smbus.SMBus(2)  
bus.write_byte(0x2A, 0x14)
avg = bus.read_byte(0x2A)

mvdifference = ((5000 / 1024 ) *  (avg-2)) 


print('Millivolts:' +(str)(mvdifference))

current = mvdifference / 185

print('Current:' + (str)(current))


