from ayn import BaseRPCServer

s = BaseRPCServer()

@s.reg
def add(a, b, c=10):
    funs = s.getfunlist()
    sum = a + b + c
    return sum

s.listen(2550)
s.server_forever()