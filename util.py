#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2014-06-30
# @Author  : Robin (sintrb@gmail.com)
# @Link    : https://github.com/sintrb/PyMITM
# @Version : 1.0

def recvall(soc):
	buflen = 65535
	data = []
	while True:
		try:
			d = soc.recv(buflen)
			data.append(d)
		except:
			d = ''
		if len(d) < buflen:
			break
		soc.settimeout(5)
	return ''.join(data)
		# if 'Content-Encoding' in headers and headers['Content-Encoding'] == 'gzip':
		# 	da = StringIO.StringIO(self.databody)
		# 	gf = gzip.GzipFile(fileobj=da)
		# 	self.databody = gf.read()
		# 	gf.close()
		# 	da.close()
		# 	del headers['Content-Encoding']