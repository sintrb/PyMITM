#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2014-07-01
# @Author  : Robin (sintrb@gmail.com)
# @Link    : https://github.com/sintrb/PyMITM/
# @Version : 1.0







if __name__ == '__main__':
	from Setting import setting
	import sys
	dnssev = DNSSpoofingServer(setting['dnsspoofing'])
	dnssev.serve_forever()