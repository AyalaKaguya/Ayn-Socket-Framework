# Ayn Socket Framework 

## Sockets组播实现

简单的基于通道的SocketServer...

说不定能写个可以对战的游戏呢？

Public 频道，承载基础指令和错误反馈，不接受json信息，如果发送json，将会触发数据路由。

## 使用文档

### 服务端

```python
from ayn import sockets_simple_server
Socket_simple_server('127.0.0.1', 2550)
```

### 客户端

```python
from ayn import sockets_simple_client

def abc(data: str):
    print(data)

Sockets_simple_client('127.0.0.1', 2550).subscribe('mro', abc).client_forver()
```

类 `SocketsClient` 的一些方法：

构造函数提供服务器的地址和端口。

method|introduce
----|----
subscribe(channelName: str, func) -> go | 订阅一个通道，提供一个回调函数，一个通道只能订阅一个回调函数。
unsubscribe(channelName: str) -> go | 退订一个通道。
client_forver() | 启动事件循环，建议使用多线程。
send(channelName: str, dataString: str) -> go | 向指定的通道发送信息。
close() | 关闭并 `删除` 连接。