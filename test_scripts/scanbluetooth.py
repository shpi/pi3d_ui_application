import os
import re


output = os.popen('sudo timeout -s INT 5s hcitool scan').readlines()

for line in output:
        out = re.search('\s*([0-9A-F]{2}\:[0-9A-F]{2}\:[0-9A-F]{2}\:[0-9A-F]{2}\:[0-9A-F]{2}\:[0-9A-F]{2})\s*([^\n]*)',line, flags=re.IGNORECASE)
        if out is not None:
                print(out.group(1))
                print(out.group(2))

output = os.popen('sudo timeout -s INT 5s hcitool lescan').readlines()

for line in output:
        out = re.search('\s*([0-9A-F]{2}\:[0-9A-F]{2}\:[0-9A-F]{2}\:[0-9A-F]{2}\:[0-9A-F]{2}\:[0-9A-F]{2})\s*([^\n]*)',line, flags=re.IGNORECASE)
        if out is not None:
                print(out.group(1))
                print(out.group(2))



