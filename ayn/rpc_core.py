import json
from .string_tcp_core import ThreadStringTCPServer, StringTCPCilent


class BaseRPCClient(StringTCPCilent):

    def raw_funcall(self, function: str, *args, **kwargs):
        '''调用远端函数，获取原始数据'''
        d = {'fn': function,
             'fa': args, 'fk': kwargs}
        self.send(json.dumps(d))  # 发送数据
        data = self.recv()  # 接收方法执行后返回的结果
        data = json.loads(data)
        return data

    def funcall(self, function: str, *args, **kwargs):
        '''就像调用函数一样，会继承远端的异常'''
        data = self.raw_funcall(function, *args, **kwargs)
        if data['err']:
            raise Exception(data['ex'])
        return data['res']

    def __getattr__(self, function):
        def _func(*args, **kwargs):
            return self.funcall(function, *args, **kwargs)

        setattr(self, function, _func)
        return _func


class BaseRPCServer(ThreadStringTCPServer):
    def __init__(self):
        super().__init__()
        self.funs = {}

    def onConnectionRequest(self, data: str, address: str, payloads: None) -> str:
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
