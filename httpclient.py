#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
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

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    def get_host_port(self,url):
        up=urllib.parse.urlparse(url)
        path=''+up.path
        if path=='':
            path='/'
        hostname=up.hostname
        port=up.port
        if not port:
            port=80
        return path,hostname,port
    
    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        return int(data.split(' ')[1])

    def get_headers(self,data):
        return data.split('\r\n\r\n')[0]

    def get_body(self, data):
        return data.split('\r\n\r\n')[1]

    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))

    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def getdata(self,path,hostname):
        pl='GET '+path+' HTTP/1.1\r\n'
        hn='Host: '+hostname+'\r\n'
        ac='Accept: */*\r\n'
        cc='Connection: close\r\n'
        return (pl+hn+ac+cc+'\r\n')

    def GET(self, url, args=None):
        body=''
        path,hostname,port=self.get_host_port(url)
        self.connect(hostname,port)
        data=self.getdata(path,hostname)
        print(data)
        self.sendall(data)
        rdata=self.recvall(self.socket)
        code=self.get_code(rdata)
        body=body+self.get_body(rdata)
        self.close()
        print(rdata)
        return HTTPResponse(code, body)

    def postdata(self,path,hostname,bd):
        pl='POST '+path+' HTTP/1.1\r\n'
        hn='Host: '+hostname+'\r\n'
        ac='Accept: */*\r\n'
        cl='Content-Length: '+str(len(bd))+'\r\n'
        ct='Content-Type: application/x-www-form-urlencoded\r\n'
        cc='Connection: close\r\n'
        return (pl+hn+ac+cl+ct+cc+'\r\n'+bd)

    def POST(self, url, args=None):
        body=''
        path,hostname,port=self.get_host_port(url)
        self.connect(hostname,port)
        bd=''
        if args:
            bd=urllib.parse.urlencode(args)
        data=self.postdata(path,hostname,bd)
        print(data)
        self.sendall(data)
        rdata=self.recvall(self.socket)
        code=self.get_code(rdata)
        body=body+self.get_body(rdata)
        self.close()
        print(rdata)
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )

if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
