PyMITM
======
A Man-in-the-Middle Attack Toolchain by Python 2.x, include DNSSpoofing(by a simple DNS Server) and SessionHijack(by a simple HTTPProxy Server).

一个Python 2.x实现的中间人攻击工具, 包括DNS欺骗（通过一个简单的DNS服务器实现）和会话劫持（通过一个简单的HTTP代理服务器实现）。

主要组件：

* DNS服务器: 通过[PyDNSServer](https://github.com/sintrb/PyMITM/blob/master/PyDNSServer.py)实现
* HTTP代理服务器: 通过[PyHTTPProxy](https://github.com/sintrb/PyMITM/blob/master/PyHTTPProxy.py)实现

怎么用？直接run吧：
```
python PyMITM.py
```

PyMITM.py自带了一个简单的配置例子，该例子完成对www.baidu.com的180度反转。
* DNS欺骗

> 首先需在路由器上设置DNS服务器为运行该程序的电脑IP（该电脑需要设置固定的DNS服务器地址，比如Google的8.8.8.8），这样就能够将接入该路由器的所有设备的DNS请求定向到该电脑上（前提是设备使用自动获取DNS服务器地址）。例子里只做了www.baidu.com的欺骗。

* 会话劫持

> HTTP会话劫持可以根据请求头或者响应头进行过滤。例子里面做了多www.baidu.com的会话劫持，对返回的页面进行180度旋转。


