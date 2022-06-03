import cmd
import string
import subprocess
import sys

from .string_tcp_core import ThreadStringTCPServer

IDENTCHARS = string.ascii_letters + string.digits + '_'


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


class BaseRCHander(cmd):
    pass

class BaseRCServer(ThreadStringTCPServer):
    def __init__(self):
        super().__init__()
        self.identchars = IDENTCHARS

    def onConnectionRequest(self, request_body: str, address: str) -> str:
        return super().onConnectionRequest(request_body, address)


