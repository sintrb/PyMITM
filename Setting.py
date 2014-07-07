#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2014-07-07
# @Author  : Robin (sintrb@gmail.com)
# @Link    : https://github.com/sintrb/PyMITM/
# @Version : 1.0

setting = {
	'dnsspoofing':{
		'listen':{
			'host':'0.0.0.0',
			'port':53,
		},
		'logging':{
			'file':'dns.log',
			'console':True,
		},
		'resolv':(
			('127.0.0.1',
				(
					('www.baidu.com','1.2.3.4'),
					('.*','111.111.111.111'),
				)
			),
			('.*',
				(
					('.*','172.16.0.1'),

				)
			)
		)
	},
	'http'
}
