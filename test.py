
autoslides = ['thermostat','weather','ical']
slides = ['thermostat','weather','status','shutter','livegraph','amperemeter','rrdgraph','ical','settings']
autoslides = ['thermostat','weather','status','shutter','livegraph','amperemeter','rrdgraph','ical','settings']

autoslideints = []

for autoslide in autoslides:
  i = 0
  for slide in slides:
     
     if slide  == autoslide:
       autoslideints.append(i)
     i += 1


for i in range(0,10):

 print(autoslideints[i % len(autoslideints)])





