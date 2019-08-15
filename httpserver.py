from http.server import BaseHTTPRequestHandler

class ServerHandler(BaseHTTPRequestHandler):

       def do_GET(self):
         global eg_object
         try:

           if "?" in self.path:
             start_time = time.time()
             message = ''
             self.send_response(200)
             self.send_header('Content-type','text')
             self.end_headers()
             print(self.client_address[0],end=': ')

             for key, value in dict(urlparse.parse_qsl(self.path.split("?")[1], True)).items():
               if key == 'lastmotion': # special treatment
                 message += '{}_date:{}_{:.1f}s_ago;'.format(
                         key,
                         time.strftime("%Y-%m-%d_%H:%M:%S", time.gmtime(eg_object.lastmotion)), 
                         time.time() - eg_object.lastmotion
                 )
               elif hasattr(eg_object, key):
                 message += '{}:{};'.format(key, getattr(eg_object, key))

                 if (value != ''):
                   try:
                     if key in ('backlight_level'):             
                       value = int(value) # variable int value
                       assert -1 < value < 32, 'value outside 0..31'

                     elif key in ('vent_pwm'):
                       value = int(value) # variable int value
                       assert -1 < value < 256, 'value outside 0..255'
 

                     else:
                       value = VALS[value] # convert from '0','1','CLICK' string
                     key_code = CODES_32U4[key] # convert to 0x87 etc
                     bus.write_byte_data(ADDR_32U4, key_code, value)
                   except Exception as e:
                     message += 'Excepton:{}>{};'.format(key, e)
                   finally:
                     message +=  '{}>{};'.format(key, value)  #we should update eg_object here?

             print(message)
             print("-- %s seconds --" % (time.time() - start_time))
             self.wfile.write(bytes(message, "utf8"))
             self.connection.close()
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
