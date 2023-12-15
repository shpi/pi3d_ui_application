def steinhart_temperature_C(r, Ro=10000.0, To=25.0, beta=3450.0):
    import math
    steinhart = math.log(Ro / r) / beta      # log(R/Ro) / beta
    steinhart += 1.0 / (To + 273.15)         # log(R/Ro) / beta + 1/To
    steinhart = (1.0 / steinhart) - 273.15   # Invert, convert to C
    return steinhart


#tempsensor = A5
#ntc = (steinhart_temperature_C(10000 / (1023/tempsensor - 1)))
  

