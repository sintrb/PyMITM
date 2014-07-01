#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2014-06-30
# @Author  : Robin (sintrb@gmail.com)
# @Link    : https://github.com/sintrb/PyMITM/blob/master/PyHTTPProxy.py
# @Version : 1.0

import re
import gzip
import socket
import StringIO
import SocketServer

class HTTPObject:
	'''
	HTTP Frame, both client request to server and server response to client
	'''
	def __init__(self, fd):
		'''
		Init a HTTP Object, fd is a fileobj of raw request or response
		'''
		self.fd = fd
		self.headers = {}
		self.databody = None

		# parse
		self.parse_header()
		self.parse_databody()

		
	def parse_header(self):
		'''
		Parse HTTP header
		'''
		fd = self.fd
		hd = []
		isfirst = True
		self.raw_firstline = self.firstline = ''
		while True:
			l = fd.readline().rstrip('\r\n')
			ix = l.find(':')
			if isfirst and l:
				self.raw_firstline = self.firstline = l
				isfirst = False
			elif ix>0:
				k = l[0:ix].strip()
				v = l[ix+1:].strip()
				hd.append((k, v),)
			if not l and not isfirst:
				break
		self.headers = dict(hd)

	def parse_databody(self):
		'''
		Read data body, maybe it's empty(such as HTTP GET Request)
		'''
		fd = self.fd
		headers= self.headers
		if 'Content-Length' in headers:
			# normal response body
			content_length = int(headers['Content-Length'])
			count = 0
			data = []
			while count < content_length:
				d = fd.read(content_length)
				if d:
					count = count + len(d)
					data.append(d)
				else:
					break
			self.databody = ''.join(data)
		elif 'Transfer-Encoding' in headers and headers['Transfer-Encoding'] == 'chunked':
			# handle chunked response
			# I have wasted nearly one day time on it, FUCK IT!!!
			data = []
			while True:
				l = int(fd.readline(), 16)	# trunk size
				if l == 0:
					fd.read(2)	# last trunk:  0\r\n\r\n
					break
				d = fd.read(l)	# read data
				fd.read(2)	# skip \r\n
				data.append(d)

			self.databody = ''.join(data)
			del headers['Transfer-Encoding']	# it will transfer all data once time, so unneccessary Transfer-Encoding
	def do_unzip(self):
		'''
		unzip the databody if the databody is a ziped data
		'''
		if 'Content-Encoding' in self.headers and self.headers['Content-Encoding'] == 'gzip':
			import StringIO, gzip
			da = StringIO.StringIO(self.databody)
			gf = gzip.GzipFile(fileobj=da)
			self.databody = gf.read()
			gf.close()
			da.close()
			del self.headers['Content-Encoding']

	def get_alldata(self):
		if self.databody:
			self.headers['Content-Length'] = len(self.databody)
		return '%s\r\n%s\r\n\r\n%s'%(self.firstline, '\r\n'.join(['%s: %s'%(k,v) for k,v in self.headers.items()]), self.databody or '')

class RequestObject(HTTPObject):
	'''
	Http Request
	'''
	def __init__(self, fd):
		HTTPObject.__init__(self, fd)
		words = self.raw_firstline.split()
		if len(words) == 3:
			self.method, self.path, self.version = words
		else:
			self.method, self.path, self.version = ('GET','/','HTTP/1.0')

		# rebuild firstline and path, 
		# because proxy path is like "http://hostname/path", but in fact only "/path"
		if re.match('http://[^/]+/\S*', self.path):
			self.path = re.findall('http://[^/]+(/\S*)', self.path)[0]
		self.firstline = ' '.join((self.method, self.path, self.version),)

		# change 'Proxy-Connection' to 'Connection'. Cheat the HTTP server? YES!
		if 'Proxy-Connection' in self.headers:
			self.headers['Connection'] = self.headers['Proxy-Connection']
			del self.headers['Proxy-Connection']

		# get reality host name and port
		# it's in headers, "Host: hostname:port"
		try:
			host = self.headers['Host']
			clix = host.find(':')
			if clix>0:
				self.hostname = host[0:clix]
				self.hostport = int(host[clix+1:])
			else:
				self.hostname = host
				self.hostport = 80	# 80 is default
		except:
			print self.raw_firstline
			print self.headers



class ResponseObject(HTTPObject):
	'''
	Http Response
	'''
	def __init__(self, fd):
		HTTPObject.__init__(self, fd)
		words = self.raw_firstline.split()
		if len(words) == 3:
			self.version, self.code, self.status = self.firstline.split()
		else:
			self.version, self.code, self.status = ('HTTP1.0', 200, 'OK')
		


class HttpProxyHandler(SocketServer.StreamRequestHandler):
	'''
	A TCP Handler to handle HTTP request
	'''
	def before_proxy(self, req):
		'''
		A hook before proxy request,
		if return True, the proxy will not goon,
		if return a instance of HTTPObject, the instance will be response to client
		if return False, proxy goon
		'''
		print req.firstline

	def after_proxy(self, req, res):
		'''
		A hook after proxy request,
		if return True, the response will not goon,
		if return False, response res to client
		'''
		print res.firstline

	def handle(self):
		'''
		Handle tcp request
		'''
		req = RequestObject(self.rfile)	# Generate a Request object From client request
		res = self.before_proxy(req)
		if not res:
			# create a socket and connect to server
			sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			sock.connect((req.hostname, req.hostport),)

			# send request data to server
			sock.send(req.get_alldata())
			#sock.settimeout(10)
			#  Generate a Response object From server response
			res = ResponseObject(sock.makefile())
			sock.close()

			if self.after_proxy(req, res):
				return

		# forward response data
		if isinstance(res, HTTPObject):
			self.wfile.write(res.get_alldata())
			self.wfile.flush()

class HttpProxyServer(SocketServer.TCPServer):
	'''
	A Base Http Proxy Server
	'''
	def __init__(self, server_address, HttpProxyHandlerClass=HttpProxyHandler, bind_and_activate=True):
		'''
		Init a Http Proxy Server,
		HttpProxyHandlerClass must be a subclass of HttpProxyHandler
		'''
		SocketServer.TCPServer.__init__(self, server_address, HttpProxyHandlerClass, bind_and_activate)

if __name__ == '__main__':
	import sys
	host, port = '0.0.0.0', len(sys.argv) == 2 and int(sys.argv[1]) or 9999
	serv = HttpProxyServer((host, port), )
	print 'Proxy Server running at %s:%s'%(host, port)
	serv.serve_forever()

