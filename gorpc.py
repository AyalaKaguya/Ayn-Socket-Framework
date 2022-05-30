import json
import socket
import threading


class RPCClient:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self, host, port):
        '''链接Server端'''
        self.sock.connect((host, port))

    def __send(self, data: str):
        '''将数据发送到Server端'''
        self.sock.send(str(len(data)).encode())  # 客户端发送长度位
        if not self.sock.recv(1024) == b'SACK':  # 服务器响应客户端
            raise Exception('abnormal sending order')
        self.sock.sendall(data.encode('utf-8'))  # 客户端发送所有数据

    def __recv(self) -> str:
        '''接受Server端回传的数据'''
        res_size = self.sock.recv(1024)  # 客户端接受长度位
        self.sock.send(b'CACK')  # 客户端响应
        resed_size = 0
        res_buff = ""
        while resed_size < int(res_size.decode()):  # 客户端接收所有数据
            res = self.sock.recv(1024)
            resed_size += len(res)
            res_buff += res.decode('utf-8')
        return res_buff

    def close(self):
        '''关闭连接'''
        self.sock.close()

    def funcall(self, function: str, *args, **kwargs):
        '''就像调用函数一样，会继承远端的异常'''
        data = self.raw_funcall(function, *args, **kwargs)
        if data['err']:
            raise Exception(data['ex'])
        return data['res']

    def raw_funcall(self, function: str, *args, **kwargs):
        '''调用远端函数，获取原始数据'''
        d = {'fn': function,
             'fa': args, 'fk': kwargs}
        self.__send(json.dumps(d))  # 发送数据
        data = self.__recv()  # 接收方法执行后返回的结果
        data = json.loads(data)
        return data

    def __getattr__(self, function):
        def _func(*args, **kwargs):
            return self.funcall(function, *args, **kwargs)

        setattr(self, function, _func)
        return _func


class RPCServer:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.funs = {}
        self.port = None

    def __accept(self):
        '''获取Client端信息，并为连接创建一个线程'''
        sock = self.sock.accept()
        t = threading.Thread(target=self.__conn, args=sock)
        t.start()

    def __conn(self, client_socket: socket.socket, address: str):
        '''连接处理函数，进入接收应答循环'''
        print("Connection from: {}".format(address))
        while True:
            try:
                req_size = client_socket.recv(1024)  # 服务器接收长度位
                if not req_size:
                    break
                client_socket.send(b'SACK')  # 服务器响应
                reqed_size = 0
                req_buff = ""
                while reqed_size < int(req_size.decode()):  # 服务器接受所有数据
                    res = client_socket.recv(1024)
                    if not res:
                        break
                    reqed_size += len(res)
                    req_buff += res.decode('utf-8')

                res = self.__call(req_buff)

                client_socket.send(str(len(res)).encode())  # 服务器发送长度位
                if not client_socket.recv(1024) == b'CACK':  # 服务器响应客户端
                    break
                client_socket.sendall(res.encode('utf-8'))  # 服务器发送所有数据
            except Exception as ex:
                print("{} caused a problem: {}".format(address, ex))
                break

    def __call(self, data: str) -> str:
        '''解析数据，调用对应的方法变将该方法执行结果返回'''
        json_data = json.loads(data)
        method_name = json_data['fn']
        method_args = json_data['fa']
        method_kwargs = json_data['fk']
        try:
            res = self.funs[method_name](*method_args, **method_kwargs)
        except KeyError as ex:
            data = {
                "err": True, "ex": f"[KeyError] The function may not be registered or a KeyError has occurred: {str(ex)}"}
        except Exception as ex:
            data = {"err": True, "ex": str(ex)}
        else:
            data = {"err": False, "res": res}
        return json.dumps(data)

    def getfunlist(self):
        return self.funs

    def reg(self, function, name=None):
        '''Server端方法注册，Client端只可调用被注册的方法'''
        if name is None:
            name = function.__name__
        self.funs[name] = function

    def listen(self, port):
        self.port = port
        self.sock.bind(('0.0.0.0', port))
        self.sock.listen(5)

    def server_forever(self):
        '''打开监听循环'''
        if self.port == None:
            raise ConnectionError("unbinding port")
        print('Server listen {} ...'.format(self.port))
        while True:
            self.__accept()


if __name__ == "__main__":
    '''实现一个简单的RPC Server'''
    s = RPCServer()

    @s.reg
    def add(a, b, c=10):
        funs = s.getfunlist()
        sum = a + b + c
        return sum
    s.listen(2550)
    s.server_forever()
