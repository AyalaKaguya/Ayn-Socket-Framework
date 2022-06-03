import subprocess
import sys
import os
from time import sleep

from .string_tcp_core import ThreadStringTCPServer, ThreadStringTCPCilent


def run_cmd(cmd_string, timeout=8):
    p = subprocess.Popen(cmd_string, stderr=subprocess.STDOUT, stdout=subprocess.PIPE, shell=True, close_fds=True,
                         start_new_session=True)

    format = 'utf-8'
    if sys.platform == "win32":
        format = 'gbk'

    try:
        (msg, errs) = p.communicate(timeout=timeout)
        ret_code = p.poll()
        if ret_code:
            code = 1
            msg = str(msg.decode(format))
        else:
            code = 0
            msg = str(msg.decode(format))
    except subprocess.TimeoutExpired:
        p.kill()
        p.terminate()
        code = 1
        msg = "RC [Timeout] : Command '" + cmd_string + \
            "' timed out after " + str(timeout) + " seconds"
    except Exception as e:
        code = 1
        msg = "RC [ERROR] : " + str(e)

    return code, msg


class BaseRCHander():
    def inputLine(self, line: str) -> str:
        try:
            cmd = line
            cmdl = cmd.split(" ")
            if cmdl[0] == "cd":
                cdd = cmd[3:]
                if cdd:
                    try:
                        os.chdir(cdd)
                    except Exception as ex:
                        return "RC [ERROR] : " + str(ex)
                return os.getcwd()
            _, result = run_cmd(cmd)
            return result
        except Exception as ex:
            return ex


class BaseRCServer(ThreadStringTCPServer):
    def __init__(self, RCHander: BaseRCHander = BaseRCHander):
        super().__init__()
        self.RCHander = RCHander
        self.MULTI_PACKET_SEND = False

    def onConnectionEnter(self, address: str) -> BaseRCHander:
        return self.RCHander()

    def onConnectionRequest(self, request_body: str, address: str, payloads: BaseRCHander) -> str:
        return payloads.inputLine(request_body)


class BaseRCClient(ThreadStringTCPCilent):
    def __init__(self):
        super().__init__()
        self.MULTI_PACKET_SEND = False

    def run(self):
        self.loop_start()
        while True:
            c = input()
            if not c:
                continue
            self.send(c)

    def onMessageReceived(self, respond_body: str) -> None:
        print(respond_body,end='')

    def send(self, data: str) -> None:
        super().send(data)
        sleep(0.2)
