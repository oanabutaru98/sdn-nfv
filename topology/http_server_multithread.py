#!/usr/bin/python3
# (C) 2022 Massimo Girondi - CC BY-NC-SA 4.0

from http.server import HTTPServer
from http.server import BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
import socket
import threading
import sys


class RequestHandler(BaseHTTPRequestHandler):

    # Generate responses with some content
    def response(self,method = "GET", code=200):
        self.send_response(code)
        self.end_headers()
        cl_a, cl_p = self.client_address
        response = "Hi "+ cl_a + ":" + str(cl_p) + "!\n"
        response += "You asked " + method +" at " + self.path +".\n"
        response += "My job here is finished.\n"
        self.wfile.write(response.encode())

    # Implement here the methods needed
    def do_GET(self):
        self.response("GET")
    def do_POST(self):
        self.response("POST")
    def do_PUT(self):
        self.response("PUT")
    def do_UPDATE(self):
        self.response("UPDATE")
    def do_DELETE(self):
        self.response("DELETE")
    def do_INSERT(self):
        self.response("INSERT")
    def do_HEAD(self):
        self.response("HEAD")
    def do_TRACE(self):
        self.response("TRACE")
    def do_CONNECT(self):
        self.response("CONNECT")
    def do_OPTIONS(self):
        self.response("OPTIONS")


# This is the class that will spawn our threads
class MultiThreadServer(ThreadingMixIn, HTTPServer):
    pass

# And here the  startup logic
if __name__ == '__main__':
    if len(sys.argv) !=2:
      port = 80
      address = "0.0.0.0"
    else:
      address, port = sys.argv[1].split(":")
    server = MultiThreadServer((address, int(port)), RequestHandler)
    server.serve_forever()
