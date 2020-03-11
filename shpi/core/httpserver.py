#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import os
import logging

try:
    from http.server import BaseHTTPRequestHandler, HTTPServer
except:
    from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

from .. import config
from . import peripherals

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

                logging.debug('http request from: ' + self.client_address[0])

                for key, value in dict(urlparse.parse_qsl(self.path.split("?")[1], True)).items():

                    if key == 'screenshot':

                        self.send_header('Content-type', 'image/png')
                        self.end_headers()
                        try:
                            os.popen('rm /media/ramdisk/screenshot.png')
                            time.sleep(0.1)
                        except:
                            pass

                        while not os.path.exists("/media/ramdisk/screenshot.png"):
                            time.sleep(0.15)

                        # self.wfile.write(screenshot.getvalue())
                        time.sleep(4)
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
                                    peripherals.control(key, value)
                                except Exception as e:
                                    message += 'Excepton:{}>{};'.format(key, e)
                                finally:
                                    # we should update eg_object here?
                                    message += '{}>{};'.format(key, value)

                        self.wfile.write(bytes(message, "utf8"))
                        self.connection.close()

                logging.info(message)
                logging.debug("request finished in:  %s seconds" %
                              (time.time() - start_time))
                #self.wfile.write(bytes(message, "utf8"))
                # self.connection.close()
            else:
                self.send_response(404)
                self.connection.close()
        except Exception as e:
            logging.warning(e)
            self.send_response(400)
            self.connection.close()

        return

    def log_request(self, code):
        pass

    def do_POST(self):
        self.do_GET()

    def end_headers(self):
        try:
            super().end_headers()
        except BrokenPipeError as e:
            self.connection.close()
            logging.error('httpserver error: {}'.format(e))
