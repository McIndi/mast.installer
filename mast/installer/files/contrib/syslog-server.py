#!/usr/bin/env python
import os
import logging
import socketserver

LOG_FILE = 'datapower_syslog.log'
HOST, PORT = "0.0.0.0", 514

logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    datefmt='',
    filename=LOG_FILE, filemode='a')


class SyslogUDPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        data = bytes.decode(self.request[0].strip())
        socket = self.request[1]
        data = "{}: {}" % self.client_address[0], str(data)
        logging.info(str(data))

if __name__ == "__main__":
	try:
		server = socketserver.UDPServer((HOST,PORT), SyslogUDPHandler)
		server.serve_forever(poll_interval=0.5)
	except (IOError, SystemExit):
		raise
	except KeyboardInterrupt:
		print("Crtl+C Pressed. Shutting down.")
