from ayn import BaseRCServer

s = BaseRCServer()

s.listen(2550)
s.server_forever()