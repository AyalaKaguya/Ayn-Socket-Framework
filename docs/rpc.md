# Ayn Socket Framework 

## 基本RPC框架文档

### 服务端示例

```python
from ayn import BaseRPCServer

s = BaseRPCServer()

@s.reg
def add(a, b, c=10):
    funs = s.getfunlist()
    sum = a + b + c
    return sum

s.listen(2550)
s.server_forever()
```

### 客户端示例
```python
from ayn import BaseRPCClient

c = BaseRPCClient()
c.connect('127.0.0.1', 2550)
res = c.add(1, 2, c=3)
print(f'res1: {res}')
res = c.funcall('add',1,2,c=3)
print(f'res2: {res}')
res = c.raw_funcall('add',1,2,c=3)
print(f'res3: {res}')
c.close()
```

### 类 `RPCServer` 的一些方法：

无参构造函数将创建一个goRPC的Server实例。

method|introduce
----|----
reg(func) -> None | 注册函数到函数列表内，只有注册过的函数才能被调用，该方法可以用于装饰器 `@<RPCServer>.reg`。
getfunlist() -> Map<str,func> | 获得所有注册的函数，面向已注册的函数内部使用。
listen(port:int) -> None | 指定监听的端口，必须先指定端口才能开启服务器循环。
server_forever() -> None | 启动服务端循环。

### 类 `RPCClient` 的一些方法：

无参构造函数将创建一个goRPC的Client实例。

method|introduce
----|----
connect(ip:str,port:int) -> None | 连接到GoRPC服务器。
funcall(func_name:str,*args,**kwargs) -> callback | 就像调用函数一样，会继承远端的异常。
raw_funcall(func_name:str,*args,**kwargs) -> jsonObject | 调用远端函数，获取原始数据。
close() -> None | 关闭客户端。
`funcName`(*args,**kwargs)  -> callback | 可以直接用远端函数的函数名作为方法调用。