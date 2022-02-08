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
from urllib.parse import urlparse


def help():
    print("httpclient.py [GET/POST] [URL]\n")


class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body


class HTTPClient(object):
    # def get_host_port(self,url):
    def get_host_port(self, url):
        # use urllib.parse to encode the url and get information
        url_content = urllib.parse.urlparse(url)
        scheme = url_content.scheme
        host = url_content.hostname
        port = url_content.port
        path = url_content.path

        # check and modify the url to make sure it is valid
        if port is None:
            port = 80
        if path == "":
            path = "/"

        return scheme, host, port, path

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        # get the code of data
        response = data.split()[1]
        code = int(response)
        return code

    def get_headers(self, data):
        # get the headers of data
        headers = data.split('\r\n\r\n')[0]
        return headers

    def get_body(self, data):
        # get the body of data
        body = data.split('\r\n\r\n')[1]
        return body

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
            if part:
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        code = 500
        body = ""

        info = self.get_host_port(url)
        scheme = info[0]
        host = info[1]
        port = info[2]
        path = info[3]

        self.connect(host, port)
        self.GetRes(path, host)

        data = self.recvall(self.socket)
        headers = self.get_headers(data)
        code = self.get_code(data)
        body = self.get_body(data)

        # print(data)

        self.close()
        return HTTPResponse(code, body)

    def GetRes(self, url_path, url_host):
        method = "GET "
        info = method + url_path + " HTTP/1.1\r\n"
        host = "Host: " + url_host + "\r\n"
        response = info + host + "Connection: close\r\n\r\n"
        self.sendall(response)

    def POST(self, url, args=None):
        code = 500
        body = ""

        info = self.get_host_port(url)
        scheme = info[0]
        host = info[1]
        port = info[2]
        path = info[3]

        self.connect(host, port)
        response = ""
        if args is not None:
            arg = urllib.parse.urlencode(args)
            length = len(arg)
            self.PostRes(path, host, length, arg)
        elif args is None:
            self.PostRes_Noargs(path, host)

        data = self.recvall(self.socket)
        print(data)
        headers = self.get_headers(data)
        code = self.get_code(data)
        body = self.get_body(data)

        self.close()
        return HTTPResponse(code, body)

    def PostRes(self, url_path, url_host, length, arguments):
        method = "POST "
        info = method + url_path + " HTTP/1.1\r\n"
        host = "Host: " + url_host + "\r\n"
        ContentType = "Content-type: application/x-www-form-urlencoded\r\n"
        ContentLength = "Content-Length: " + str(length) + "\r\n"
        response = info + host + ContentType + ContentLength + "Connection: close\r\n\r\n" + arguments + "\r\n\r\n"
        # print(response)
        self.sendall(response)

    def PostRes_Noargs(self, url_path, url_host):
        method = "POST "
        info = method + url_path + " HTTP/1.1\r\n"
        host = "Host: " + url_host + "\r\n"
        ContentType = "Content-type: application/x-www-form-urlencoded\r\n"
        ContentLength = "Content-Length: 0\r\n"
        response = info + host + ContentType + ContentLength + "Connection: close\r\n\r\n"
        # print(response)
        self.sendall(response)

    def command(self, url, command="GET", args=None):
        if command == "POST":
            return self.POST(url, args)
        else:
            return self.GET(url, args)


if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if len(sys.argv) <= 1:
        help()
        sys.exit(1)
    elif len(sys.argv) == 3:
        print(client.command(sys.argv[2], sys.argv[1]))
    else:
        print(client.command(sys.argv[1]))

# https://docs.python.org/3/library/urllib.parse.html
# https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers
# https://www.knowledgehut.com/blog/programming/sys-argv-python-examples
# https://www.urlencoder.io/python/
# https://github.com/Amos-lii/CMPUT404-assignment-web-client/blob/master/httpclient.py
# https://github.com/Scott-Dupasquier/CMPUT404-assignment-web-client/blob/master/httpclient.py
# https://github.com/ChrisChrisLoLo/CMPUT404-assignment-web-client/blob/master/httpclient.py
