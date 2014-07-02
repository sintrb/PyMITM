#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2014-07-01
# @Author  : Robin (sintrb@gmail.com)
# @Link    : https://github.com/sintrb/PyMITM/
# @Version : 1.0


from PyHTTPProxy import HttpProxyHandler, HttpProxyServer

import random

jokecsses = ['''
<style type="text/css">
.sin-joke {
   filter:progid:DXImageTransform.Microsoft.BasicImage(rotation=2);
   -moz-transform: rotate(180deg);
   -o-transform: rotate(180deg);
   -webkit-transform: rotate(180deg);
   transform: rotate(180deg);
}
</style>
''',

'''
<style type="text/css">
.sin-joke {

}
</style>
''',
]


class  HTMLInject(HttpProxyHandler):
	def before_proxy(self, req):
		print req.hostname + ' ' + req.firstline

	def after_proxy(self, req, res):
		print res.firstline
		if res.databody and 'Content-Type' in res.headers and 'text/html' in res.headers['Content-Type']:
			print 'can Inject'
			res.do_unzip()
			try:
				res.databody = res.databody.replace('</head>', '%s</head>'%random.choice(jokecsses))
				res.databody = res.databody.replace('<body', '<body class="sin-joke"')
			except:
				print res.databody
			print res.databody.find('</head>')
			
			if 'Last-Modified' in req.headers:
				del req.headers['Last-Modified']

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
	serv = HttpProxyServer((host, port), HTMLInject)
	print 'Proxy Server running at %s:%s'%(host, port)
	serv.serve_forever()