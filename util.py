#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2014-06-30
# @Author  : Robin (sintrb@gmail.com)
# @Link    : https://github.com/sintrb/PyMITM
# @Version : 1.0

def getselfidp():
	import socket
	return socket.gethostbyname(socket.gethostname())