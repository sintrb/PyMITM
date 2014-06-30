#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2014-06-30
# @Author  : Robin (sintrb@gmail.com)
# @Link    : https://github.com/sintrb/PyMITM
# @Version : 1.0

import SocketServer
import socket
import re
from util import recvall

cache = {}

class HttpRequest(object):
	'''
	HTPP Request Object
	'''
	def __init__(self, rawdata):
		self.rawdata = rawdata
		self.method, self.path, self.protocol = re.findall('(\S+)\s+(\S+)\s+(HTTP\S+)',rawdata)[0]
		nlix = rawdata.find('\r\n\r\n')
		if nlix > 0:
			self.data = rawdata[nlix+4:]
			self.headdata = rawdata[0:nlix]
		else:
			self.data = ''
			self.headdata = rawdata
		self.headers = {}
		for k,v in re.findall('(\S+):\s*(\S+)',self.headdata):
			self.headers[k.upper().replace('-','_')] = v
		# self.host, self.port = 
		host = self.headers['HOST']
		clix = host.find(':')
		if clix>0:
			self.hostname = host[0:clix]
			self.hostport = int(host[clix+1:])
		else:
			self.hostname = host
			self.hostport = 80

		print self.path
		

class HttpProxyHandler(SocketServer.BaseRequestHandler):
	'''
	A TCP Handler to handle HTTP request
	'''
	def handle(self):
		data = recvall(self.request)
		msg = None
		if re.match('\S+\s+\S+\s+HTTP\S+', data):
			req = HttpRequest(data)
			global cache
			if not req.path in cache:
				sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				sock.connect((req.hostname, req.hostport))
				sock.send(data)
				data = recvall(sock)
				sock.close()
				
				cache[req.path] = data
			else:
				data = cache[req.path]
		else:
			# not a http request
			msg = 'not a http request'
		if msg:
			data = 'HTTP/1.1 200 OK\r\nContent-Type: text/html;charset=utf-8\r\n\r\n<center>%s<center>'%msg
		self.request.sendall(data)


if __name__ == '__main__':
	host, port = '0.0.0.0', 9999
	serv = SocketServer.TCPServer((host, port), HttpProxyHandler)

	serv.serve_forever()
