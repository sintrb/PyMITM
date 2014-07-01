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
		return False
		if res.databody and 'Content-Type' in res.headers and res.headers['Content-Type'] == 'text/html':
			print 'can InjectJS'
			res.do_unzip()
			js = '<script>alert("hello");</script></head>'
			try:
				res.databody = res.databody.replace('</head>', js)
			except:
				print res.databody
			print res.databody.find('</head>')
		

cache = {}

class  HackPic(HttpProxyHandler):
	def before_proxy(self, req):
		# print req.hostname + ' ' + req.firstline
		if 'If-Modified-Since' in req.headers:
			del req.headers['If-Modified-Since']
		ck = req.hostname + req.path
		print ck
		if ck in cache:
			print 'cache'
			return cache[ck]
		else:
			print 'request'
		
	def after_proxy(self, req, res):
		print res.firstline
		if res.databody and 'Content-Type' in res.headers and res.headers['Content-Type'] in ['image/jpeg', 'image/jpg', 'image/png']:
			content_type = res.headers['Content-Type']
			res.do_unzip()
			from PIL import Image
			import StringIO, base64
			im = Image.open(StringIO.StringIO(res.databody))
			out = im.transpose(Image.ROTATE_180)
			of = StringIO.StringIO()
			out.save(of, content_type[content_type.index('/')+1:])
			of.seek(0)
			res.databody = of.read()
			ck = req.hostname + req.path
			cache[ck] = res



if __name__ == '__main__':
	import sys
	host, port = '0.0.0.0', len(sys.argv) == 2 and int(sys.argv[1]) or 9999
	serv = HttpProxyServer((host, port), HackPic)
	print 'Proxy Server running at %s:%s'%(host, port)
	serv.serve_forever()