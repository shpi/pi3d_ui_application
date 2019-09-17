from http.server import BaseHTTPRequestHandler
import time
import urllib.parse as urlparse

import core.peripherals as peripherals

from io import BytesIO
from PIL import Image
import pi3d


class ServerHandler(BaseHTTPRequestHandler):

       def do_GET(self):
         
         try:

           if "?" in self.path:
             start_time = time.time()
             message = ''
             self.send_response(200)
             
             print(self.client_address[0],end=': ')

             for key, value in dict(urlparse.parse_qsl(self.path.split("?")[1], True)).items():


              if key == 'screenshot':
               self.send_header('Content-type','image/png')
               self.end_headers()
               byte_io = BytesIO()
               img = pi3d.util.Screenshot.screenshot()
               im = Image.frombuffer('RGB', (800, 480), img, 'raw', 'RGB', 0, 1)
               im.save(byte_io, format='PNG', quality=90)
               self.wfile.write(byte_io.getvalue())



              else:
               self.send_header('Content-type','text')
               self.end_headers()
               if key == 'lastmotion': # special treatment
                 message += '{}_date:{}_{:.1f}s_ago;'.format(
                         key,
                         time.strftime("%Y-%m-%d_%H:%M:%S", time.gmtime(peripherals.eg_object.lastmotion)), 
                         time.time() - peripherals.eg_object.lastmotion
                 )
               elif hasattr(peripherals.eg_object, key):
                 message += '{}:{};'.format(key, getattr(peripherals.eg_object, key))

                 if (value != ''):
                   try:                             #its better to split in different functions, to achieve easier compatibility with shpi lite
                     if key in ('backlight_level'):             
                       value = int(value) # variable int value
                       assert -1 < value < 32, 'value outside 0..31'
                       peripherals.controlbacklight(value)
                       
                     elif key in ('vent_pwm'):
                       value = int(value) # variable int value
                       assert -1 < value < 256, 'value outside 0..255'
                       peripherals.controlvent(value)
                       
                     elif key in ('led'):
                       value = value.split(',') # variable int value
                       peripherals.controlled(value)  

                     elif key in ('alert'):
                       peripherals.eg_object.alert = int(value)
                         


                     elif key in ('buzzer'):
                       value = int(value)
                       peripherals.controlrelays(4,value)  
  
                     else:
                      if  key.startswith('relais'):
                         channel = int(key[-1])
                         peripherals.controlrelays(channel,(int)(value))
                   except Exception as e:
                     message += 'Excepton:{}>{};'.format(key, e)
                   finally:
                     message +=  '{}>{};'.format(key, value)  #we should update eg_object here?

               self.wfile.write(bytes(message, "utf8"))
               self.connection.close()

             print(message)
             print("-- %s seconds --" % (time.time() - start_time))
             #self.wfile.write(bytes(message, "utf8"))
             #self.connection.close()
           else:
             self.send_response(404)
             self.connection.close()
         except Exception as e:
           print(e)
           self.send_response(400)
           self.connection.close()

         return

       def log_request(self, code):
         pass

       def do_POST(self):
         do_GET(self)




       def end_headers(self):
         try:
           super().end_headers()
         except BrokenPipeError as e:
           self.connection.close()
