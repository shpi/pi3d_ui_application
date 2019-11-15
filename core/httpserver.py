try:
    from http.server import BaseHTTPRequestHandler, HTTPServer
except:
    from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer


import time
import core.peripherals as peripherals
import config
import os

try:
    import urlparse
except:
    import urllib.parse as urlparse


class ServerHandler(BaseHTTPRequestHandler):

    def do_GET(self):

        try:

            if "?" in self.path:
                start_time = time.time()
                message = ''
                self.send_response(200)

                print(self.client_address[0])

                for key, value in dict(urlparse.parse_qsl(self.path.split("?")[1], True)).items():

                    if key == 'screenshot':

                        self.send_header('Content-type', 'image/png')
                        self.end_headers()
                        os.popen('rm /media/ramdisk/screenshot.png')
                        time.sleep(0.01)
                        while (os.path.exists("/media/ramdisk/screenshot.png") == False):
                            time.sleep(0.1)
                        # self.wfile.write(screenshot.getvalue())
                        with open('/media/ramdisk/screenshot.png', 'rb') as content_file:
                            self.wfile.write(content_file.read())

                    else:
                        self.send_header('Content-type', 'text')
                        self.end_headers()
                        if key == 'lastmotion':  # special treatment
                            message += '{}_date:{}_{:.1f}s_ago;'.format(
                                key,
                                time.strftime(
                                    "%Y-%m-%d_%H:%M:%S", time.gmtime(peripherals.eg_object.lastmotion)),
                                time.time() - peripherals.eg_object.lastmotion
                            )
                        elif key == 'all':
                            for subkey in peripherals.eg_object.__dict__:
                                message += '{}:{};'.format(
                                    subkey, getattr(peripherals.eg_object, subkey))

                        elif hasattr(peripherals.eg_object, key):
                            message += '{}:{};'.format(key,
                                                       getattr(peripherals.eg_object, key))

                            if (value != ''):
                                try:  # its better to split in different functions, to achieve easier compatibility with shpi lite
                                    if key in ('backlight_level'):
                                        # variable int value
                                        value = int(value)
                                        assert -1 < value < 32, 'value outside 0..31'
                                        peripherals.controlbacklight(value)

                                    elif key in ('vent_pwm'):
                                        # variable int value
                                        value = int(value)
                                        assert -1 < value < 256, 'value outside 0..255'
                                        peripherals.controlvent(value)

                                    elif key in ('slide'):
                                        # variable int value
                                        value = int(value)
                                        assert - \
                                            1 < value < len(
                                                config.slides), 'value outside 0..255'
                                        peripherals.eg_object.slide = value

                                    elif key in ('led'):
                                        # variable int value
                                        value = value.split(',')
                                        peripherals.controlled(value)

                                    elif key in ('alert'):
                                        peripherals.eg_object.alert = int(
                                            value)

                                    elif key in ('buzzer'):
                                        value = int(value)
                                        peripherals.controlrelays(4, value)

                                    else:
                                        if key.startswith('relais'):
                                            channel = int(key[-1])
                                            peripherals.controlrelays(
                                                channel, (int)(value))
                                except Exception as e:
                                    message += 'Excepton:{}>{};'.format(key, e)
                                finally:
                                    # we should update eg_object here?
                                    message += '{}>{};'.format(key, value)

                        self.wfile.write(bytes(message, "utf8"))
                        self.connection.close()

                print(message)
                print("-- %s seconds --" % (time.time() - start_time))
                #self.wfile.write(bytes(message, "utf8"))
                # self.connection.close()
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
