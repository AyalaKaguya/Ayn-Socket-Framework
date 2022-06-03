import socket
import threading

MULTI_PACKET_SEND = True
SINGLE_PACKET_SIZE = 1024


class StringTCPCilent:
    '''通过字符串来传输信息的基本客户端'''

    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.isConnected = False
        self.MULTI_PACKET_SEND = MULTI_PACKET_SEND
        self.SINGLE_PACKET_SIZE = SINGLE_PACKET_SIZE

    def connect(self, host, port) -> None:
        '''链接Server端'''
        self.sock.connect((host, port))
        self.isConnected = True

    def send(self, data: str) -> None:
        '''将数据发送到Server端'''
        if self.MULTI_PACKET_SEND:
            self.sock.send(str(len(data)).encode())  # 客户端发送长度位
            if not self.sock.recv(1024) == b'SACK':  # 服务器响应客户端
                raise ConnectionError('abnormal sending order')
        self.sock.sendall(data.encode('utf-8'))  # 客户端发送所有数据

    def recv(self) -> str:
        '''接受Server端回传的数据'''
        if self.MULTI_PACKET_SEND:
            res_size = self.sock.recv(1024)  # 客户端接受长度位
            self.sock.send(b'CACK')  # 客户端响应
            resed_size = 0
            res_buff = ""
            while resed_size < int(res_size.decode()):  # 客户端接收所有数据
                res = self.sock.recv(1024)
                resed_size += len(res)
                res_buff += res.decode('utf-8')
            return res_buff
        else:
            return self.sock.recv(self.SINGLE_PACKET_SIZE).decode('utf-8')

    def close(self):
        '''关闭连接'''
        self.send('EXIT')
        self.sock.close()
        self.isConnected = False


class ThreadStringTCPCilent(StringTCPCilent):
    '''通过字符串来传输信息的基本多线程客户端'''

    def __init__(self):
        super().__init__()
        self.t_recv = threading.Thread(target=self._recv_loop, daemon=True)

    def loop_start(self) -> None:
        self.t_recv.start()

    def _recv_loop(self) -> None:
        while self.isConnected:
            try:
                res = self.recv()
                if not res:
                    break
                self.onMessageReceived(res)
            except Exception as ex:
                if self.onExceptionOccured(ex):
                    break
        self.onThreadExit()

    def onExceptionOccured(self, ex) -> bool:
        '''执行错误处理，决定线程是否退出'''
        print("An exception occured: ", ex)
        return True

    def onMessageReceived(self, respond_body: str) -> None:
        '''当子线程接收到信息时'''
        print(respond_body)

    def onThreadExit(self) -> None:
        '''当子线程退出时，连接应当终止'''
        self.close()


class StringTCPServer:
    '''通过字符串来传输信息的基本服务端'''

    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.port = None
        self.MULTI_PACKET_SEND = MULTI_PACKET_SEND
        self.SINGLE_PACKET_SIZE = SINGLE_PACKET_SIZE

    def listen(self, port) -> None:
        '''设置监听端口'''
        self.port = port
        self.sock.bind(('0.0.0.0', port))
        self.sock.listen(5)

    def server_forever(self) -> None:
        '''打开监听循环'''
        if self.port == None:
            raise ConnectionError("unbinding port")
        print('Server listen {} ...'.format(self.port))
        while True:
            self.accept()

    def accept(self) -> None:
        '''进入连接循环'''
        sock = self.sock.accept()
        self.conn(*sock)

    def conn(self, client_socket: socket.socket, address: str) -> None:
        '''连接处理函数，进入客户端接收应答循环'''
        payloads = self.onConnectionEnter(address)
        while True:
            try:
                req = self.recv(client_socket)
                if req == 'EXIT':
                    break
                res = self.onConnectionRequest(req, address, payloads)
                self.send(client_socket, res)
            except Exception as ex:
                self.onConnectionError(ex, address)
                break
        self.onConnectionExit(address, payloads)

    def send(self, sock: socket.socket, data: str) -> None:
        '''发送信息'''
        if self.MULTI_PACKET_SEND:
            sock.send(str(len(data)).encode())
            if not sock.recv(1024) == b'CACK':
                raise ConnectionError('abnormal sending order')
        sock.sendall(data.encode('utf-8'))

    def recv(self, sock: socket.socket) -> str:
        '''接收信息'''
        if self.MULTI_PACKET_SEND:
            res_size = sock.recv(1024)
            if not res_size:
                raise ConnectionError("abnormal response")
            sock.send(b'SACK')
            resed_size = 0
            res_buff = ""
            while resed_size < int(res_size.decode()):
                res = sock.recv(1024)
                if not res:
                    raise ConnectionError("abnormal response")
                resed_size += len(res)
                res_buff += res.decode('utf-8')
            return res_buff
        else:
            return sock.recv(self.SINGLE_PACKET_SIZE).decode('utf-8')

    def onConnectionEnter(self, address: str) -> object:
        print("Connection from: {}".format(address))
        return None

    def onConnectionRequest(self, request_body: str, address: str, payloads: object) -> str:
        return f"Hello {request_body} from {address}!"

    def onConnectionError(self, ex: Exception, address: str) -> None:
        print(f"{address} caused a problem: {ex}")

    def onConnectionExit(self, address: str, payloads: object) -> None:
        print("Disconnect: {}".format(address))


class ThreadStringTCPServer(StringTCPServer):
    '''通过字符串来传输信息的基本多线程服务端'''

    def accept(self) -> None:
        '''获取Client端信息，并为连接创建一个线程'''
        sock = self.sock.accept()
        t = threading.Thread(target=self.conn, args=sock)
        t.start()
