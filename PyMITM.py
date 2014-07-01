#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2014-07-01
# @Author  : Robin (sintrb@gmail.com)
# @Link    : https://github.com/sintrb/PyMITM/
# @Version : 1.0


from PyHTTPProxy import HttpProxyHandler, HttpProxyServer

class  InjectJS(HttpProxyHandler):
	def after_proxy(self, req, res):
		print res.firstline
		if 'Content-Type' in res.headers and res.headers['Content-Type'] == 'text/html':
			print 'can InjectJS'
		







if __name__ == '__main__':
	import sys
	host, port = '0.0.0.0', len(sys.argv) == 2 and int(sys.argv[1]) or 9999
	serv = HttpProxyServer((host, port), InjectJS)
	print 'Proxy Server running at %s:%s'%(host, port)
	serv.serve_forever()