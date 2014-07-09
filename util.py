#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2014-06-30
# @Author  : Robin (sintrb@gmail.com)
# @Link    : https://github.com/sintrb/PyMITM
# @Version : 1.0

import re
def getselfidp():
	import socket
	return socket.gethostbyname(socket.gethostname())


def match(p, s):
	r = p == s or re.match(p, s)
	# if r:
	# 	print '%s == %s'%(p,s)
	# else:
	# 	print '%s != %s'%(p,s)
	return r

def match_in_dic(d, pk, s):
	if not pk in d:
		return True
	else:
		return match(d[pk], s)