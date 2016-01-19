#! /usr/bin/python
#  coding: utf-8 
import SocketServer
import mimetypes
from time import gmtime, strftime
import os.path

# Copyright 2013 Abram Hindle, Eddie Antonio Santos, Kyle Hayward
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(SocketServer.BaseRequestHandler):
    uri = "./www"
    status_codes = {200: "HTTP/1.1 200 OK\r\n",
                    302: "HTTP/1.1 302 FOUND\r\n",
                    404: "HTTP/1.1 404 NOT FOUND\r\n",
                    501: "HTTP/1.1 501 NOT IMPLEMENTED\r\n"}


    def handle(self):
        self.data = self.request.recv(1024).strip()
        self.parse_request()

    def parse_request(self):
        request = self.data.split()[0]
        if request == "GET":
            self.do_get()
        else :
            self.status = 501
            self.response()
        

    def do_get(self):
        request = self.data.split('\r\n')[0]
        path = request.split()[1]
        self.uri_validate(path)
        self.response()        

    def uri_validate(self, path):
        secure = self.anti_backup(path)
        if os.path.isdir(self.uri + path) and secure:
            if path.endswith("/"):
                self.uri = self.uri + path + "index.html"
                self.status = 200
            else:
                self.uri = path + "/"
                self.status = 302
        elif os.path.isfile(self.uri + path) and secure:
            self.uri = self.uri + path
            self.status = 200
        else:
            self.status = 404

    def anti_backup(self, path):
        input_path = os.path.abspath(self.uri + path).split("/")
        root_path = os.path.abspath(self.uri).split("/")
        if root_path == input_path[:len(root_path)]:
            return True
        else:
            return False
            
    def response(self):
        date = "Date: " + strftime("%a, %d %b %Y %X GMT", gmtime()) + "\r\n"
        if self.status == 200:
            content = open(self.uri, "r").read()
            content_length = "Content-Length: %d\r\n" % len(content)
            content_type = 'Content-Type: %s\r\n\r\n' % mimetypes.guess_type(self.uri)[0]
            self.request.send(self.status_codes[self.status] + date + content_length +
                              content_type + content)
        elif self.status == 302:
            self.request.send(self.status_codes[self.status] + "Location: " + self.uri + "\r\n")
        else:
            self.request.send(self.status_codes[self.status] + date +  "\r\n")

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    SocketServer.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = SocketServer.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
