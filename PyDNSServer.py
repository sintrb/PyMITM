#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2014-06-30
# @Author  : Robin (sintrb@gmail.com)
# @Link    : https://github.com/sintrb/PyMITM
# @Version : 1.0

import SocketServer
import struct
import re
import datetime
import socket as socketlib

# DNS Query
class SinDNSQuery:
	def __init__(self, data):
		i = 1
		self.name = ''
		while True:
			d = ord(data[i])
			if d == 0:
				break;
			if d < 32:
				self.name = self.name + '.'
			else:
				self.name = self.name + chr(d)
			i = i + 1
		self.querybytes = data[0:i + 1]
		(self.type, self.classify) = struct.unpack('>HH', data[i + 1:i + 5])
		self.len = i + 5
	def getbytes(self):
		return self.querybytes + struct.pack('>HH', self.type, self.classify)

# DNS Answer RRS
# this class is also can be use as Authority RRS or Additional RRS 
class SinDNSAnswer:
	def __init__(self, ip):
		self.name = 49164
		self.type = 1
		self.classify = 1
		self.timetolive = 190
		self.datalength = 4
		self.ip = ip
	def getbytes(self):
		res = struct.pack('>HHHLH', self.name, self.type, self.classify, self.timetolive, self.datalength)
		s = self.ip.split('.')
		res = res + struct.pack('BBBB', int(s[0]), int(s[1]), int(s[2]), int(s[3]))
		return res

# DNS frame
# must initialized by a DNS query frame
class SinDNSFrame:
	def __init__(self, data):
		(self.id, self.flags, self.quests, self.answers, self.author, self.addition) = struct.unpack('>HHHHHH', data[0:12])
		self.query = SinDNSQuery(data[12:])
	def getname(self):
		return self.query.name
	def setip(self, ip):
		self.answer = SinDNSAnswer(ip)
		self.answers = 1
		self.flags = 33152
	def getbytes(self):
		res = struct.pack('>HHHHHH', self.id, self.flags, self.quests, self.answers, self.author, self.addition)
		res = res + self.query.getbytes()
		if self.answers != 0:
			res = res + self.answer.getbytes()
		return res

# A UDPHandler to handle DNS query
class SinDNSUDPHandler(SocketServer.BaseRequestHandler):
	def handle(self):
		data = self.request[0].strip()
		dns = SinDNSFrame(data)
		socket = self.request[1]
		namemap = SinDNSServer.namemap
		if(dns.query.type==1):
			# If this is query a A record, then response it
			
			name = dns.getname();
			toip = None
			ifrom = "map"
			if name in namemap:
				# If have record, response it
				toip = namemap[name]
			elif '*' in namemap:
				# Response default address
				toip = namemap['*']
			else:
				try:
					# query from standard DNS Server
					# adn response
					toip = socketlib.getaddrinfo(name,0)[0][4][0]
					ifrom = "sev"
				except:
					# query fail
					ifrom = 'fail'
			if toip:
				dns.setip(toip)
			socket.sendto(dns.getbytes(), self.client_address)
			print '%s %s > %s (%s)'%(self.client_address[0], name, toip, ifrom)
		else:
			# If this is not query a A record, ignore it
			socket.sendto(data, self.client_address)

# DNS Server
# It only support A record query
# user it, U can create a simple DNS server
class SinDNSServer:
	def __init__(self, port=53):
		SinDNSServer.namemap = {}
		self.port = port
	def addname(self, name, ip):
		SinDNSServer.namemap[name] = ip
	def start(self):
		HOST, PORT = "0.0.0.0", self.port
		server = SocketServer.UDPServer((HOST, PORT), SinDNSUDPHandler)
		server.serve_forever()

# Now, test it
if __name__ == "__main__":
	sev = SinDNSServer()
	sev.addname('www.aa.com', '192.168.0.1')	# add a A record
	sev.addname('www.bb.com', '192.168.0.2')	# add a A record
	sev.addname('*', '127.0.0.1') # default address
	sev.start() # start DNS server

# Now, U can use "nslookup" command to test it
# Such as "nslookup - 127.0.0.1" or "nslookup www.aa.com 127.0.0.1"

