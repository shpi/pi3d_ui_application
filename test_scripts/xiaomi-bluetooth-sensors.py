#!/usr/bin/env python2
#import binascii
#import base64
import os
import re
import time
from struct import unpack
import rrdtool
'''
rrdtool create bluesensors.rrd \
--step 60 \
DS:mitemp:GAUGE:120:-127:127 \
DS:mihum:GAUGE:120:0:100 \
DS:flowertemp:GAUGE:120:-127:127 \
DS:flowermois:GAUGE:120:0:100 \
DS:flowerlight:GAUGE:120:0:100000 \
DS:flowercond:GAUGE:120:0:1000 \
RRA:MAX:0.5:1:1500 \
RRA:MAX:0.5:10:1500 \
RRA:MAX:0.5:60:1500 \





rrdtool graph tempday.png \
  --start -1h \
  DEF:mitemp=bluesensors.rrd:mitemp:AVERAGE \
  LINE2:mitemp#00FF00:MI \
  VDEF:mitemplast=mitemp,LAST \
  "GPRINT:mitemplast:%.1lf C" \
  DEF:flowertemp=bluesensors.rrd:flowertemp:AVERAGE \
  LINE2:flowertemp#0000FF:Flower \
  VDEF:flowertemplast=flowertemp,LAST \
  "GPRINT:flowertemplast:%.1lf C"
'''


output = os.popen('timeout 10 gatttool -b C4:7C:8D:65:B7:CF --char-write-req -a 0x33 -n A01F').readline()
output = os.popen('timeout 10 gatttool -b C4:7C:8D:65:B7:CF --char-read -a 0x35').readline()


output = re.search('Characteristic value/descriptor:\s*([0-9A-Fa-f\ ]*)',output)
output = bytearray.fromhex(output.group(1))
temp, light, moisture, conductivity =  unpack('<hxIBhxxxxxx', output)

temp = temp / 10.0
print(temp)

output = os.popen('timeout 10 gatttool -b 4c:65:a8:d0:81:70 --char-write-req --handle=0x0010 --value=0100 --listen').readlines()[-1]
output = re.search('Notification handle = 0x000e value:\s*([0-9A-Fa-f\ ]*)',output)
output = bytearray.fromhex(output.group(1)).decode()


output = re.search('T=([0-9\.]*)\s*H=([0-9\.]*)',output)



rrdtool.update('bluesensors.rrd', 'N:%s:%s:%s:%s:%s:%s' %(output.group(1),output.group(2),temp,moisture,light,conductivity));

