PyMITM
======
A Man-in-the-Middle Attack Toolchain by Python 2.x, include DNSSpoofing(by a simple DNS Server) and SessionHijack(by a simple HTTPProxy Server).

一个Python 2.x实现的中间人攻击工具, 包括DNS欺骗（通过一个简单的DNS服务器实现）和会话劫持（通过一个简单的HTTP代理服务器实现）。

主要组件：

* DNS服务器: 通过[PyDNSServer](./blob/master/PyDNSServer.py)实现
* HTTP代理服务器: 通过[PyHTTPProxy](./blob/master/PyHTTPProxy.py)实现

