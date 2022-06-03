from ayn import BaseRCClient

c = BaseRCClient()

c.connect('127.0.0.1', 2550)
c.loop_start()

while c.isConnected:
    i = input()
    if not i:
        continue
    c.send(i)