#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2014-07-07
# @Author  : Robin (sintrb@gmail.com)
# @Link    : https://github.com/sintrb/PyMITM/
# @Version : 1.0

from PyHTTPProxy import HttpProxyHandler, HttpProxyServer
from PyDNSServer import DNSQueryHandler, DNSServer
from util import match, match_in_dic

class DNSSpoofingHandler(DNSQueryHandler):
	def spoofing(self, hostname, dns, rawdata, sock):
		fromip = self.client_address[0]
		for ipp,rev in self.server.resolvs:
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
		self.resolvs = self.setting['resolvs']
		self.logging = self.setting['logging']

		self.log_console = not ('console' in self.logging and not self.logging['console'])
		self.log_file = 'file' in self.logging and open(self.logging['file'], 'a+')
		host = setting['listen']['host']
		port = setting['listen']['port']
		DNSServer.__init__(self,server_address=(host, port),DNSQueryHandlerClass=DNSSpoofingHandler)
		print 'DNS Spoofing Server running at %s:%s'%(host, port)




class HttpHijackHandler(HttpProxyHandler):
	def match_rehijack(self,req,hijack):
		return match_in_dic(hijack, 'host', req.hostname) and match_in_dic(hijack, 'method', req.method) and match_in_dic(hijack, 'path', req.path)
	def match_headers(self,headers,hijackheaders):
		for k,v in hijackheaders.items():
			if not k in headers or not match(v,headers[k]):
				return False
		return True

	def before_proxy(self, req):
		for hijack in self.server.hijacks:
			self.is_ipmatch = match_in_dic(hijack, 'ip', self.client_address[0])
			self.is_request = 'request' in hijack and 'handler' in hijack['request'] and hijack['request']['handler']
			self.is_rematch = self.match_rehijack(req, hijack)
			self.is_reqheadersmatch = not 'headers' in hijack['request'] or self.match_headers(req.headers, hijack['request']['headers'])
			if self.is_ipmatch and self.is_request and self.is_rematch and self.is_reqheadersmatch:
				return hijack['request']['handler'](self, req)
				
	def after_proxy(self, req, res):
		for hijack in self.server.hijacks:
			self.is_ipmatch = match_in_dic(hijack, 'ip', self.client_address[0])
			self.is_response = 'response' in hijack and 'handler' in hijack['response'] and hijack['response']['handler']
			self.is_rematch = self.match_rehijack(req, hijack)
			self.is_resheadersmatch = not 'headers' in hijack['response'] or self.match_headers(res.headers, hijack['response']['headers'])
			if self.is_ipmatch and self.is_response and self.is_rematch and self.is_resheadersmatch:
				return hijack['response']['handler'](self, req, res)

class HttpHijackServer(HttpProxyServer):
	def __init__(self, setting):
		self.setting = setting
		self.hijacks = setting['hijacks']
		self.logging = self.setting['logging']

		self.log_console = not ('console' in self.logging and not self.logging['console'])
		self.log_file = 'file' in self.logging and open(self.logging['file'], 'a+')
		host = setting['listen']['host']
		port = setting['listen']['port']
		HttpProxyServer.__init__(self,server_address=(host, port),HttpProxyHandlerClass=HttpHijackHandler)
		print 'Http Hijack Server running at %s:%s'%(host, port)
		
		

