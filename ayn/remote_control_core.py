import os
import socketserver
import subprocess
import sys
import ctypes
from socket import *

# whnd = ctypes.windll.kernel32.GetConsoleWindow()
# hide = "--hide" in sys.argv

debug = "--debug" in sys.argv


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
        msg = "goRC [Timeout] : Command '" + cmd_string + \
            "' timed out after " + str(timeout) + " seconds"
    except Exception as e:
        code = 1
        msg = "goRC [ERROR] : " + str(e)

    return code, msg


class goRCServer(socketserver.BaseRequestHandler):
    def handle(self):
        while True:
            try:
                data = self.request.recv(2048).decode("utf-8")
                if not data:
                    if debug:
                        print("goRC [ERROR] : 远程主机非正常退出或错误")
                    break
                cmd = data.replace("EOF", "")
                cmdl = cmd.split(" ")
                if debug:
                    print("goRC [cmd]:", cmd)
                if cmdl[0] == "cd":
                    cdd = cmd[3:]
                    if cdd:
                        try:
                            os.chdir(cdd)
                        except Exception as ex:
                            self.request.sendall(
                                ("goRC [ERROR] : " + str(ex)).encode("utf-8"))
                    self.request.sendall(os.getcwd().encode("utf-8"))
                    continue
                _, result = run_cmd(cmd)
                self.request.sendall(result.encode("utf-8"))
            except Exception as ex:
                if debug:
                    print(ex)
                break


tcp_client = socket(AF_INET, SOCK_STREAM)


def cilent_forever(ip):
    while True:
        send("cd")
        pwd = tcp_client.recv(2048).decode("utf-8").replace("\r\n", "")
        title = "goRC [{}] : {}".format(ip, pwd)
        ctypes.windll.kernel32.SetConsoleTitleW(title)
        prompt = "{} {}>".format("goRC", pwd)
        msg = input(prompt).strip()
        if not msg:
            continue
        if msg == "exit":
            tcp_client.close()
            break
        send(msg)
        data = tcp_client.recv(20480)
        print(data.decode("utf-8"))


def send(cmdstr):
    tcp_client.sendall("{}{}".format(cmdstr, "EOF").encode("utf-8"))


def remote_control_simple_client(serv: str, port: int):
    ip_port = (serv, port)
    tcp_client.connect(ip_port)
    cilent_forever(serv)
    tcp_client.close()


def remote_control_simple_server(serv: str, port: int):
    print("service start at", serv)
    # if whnd != 0 and not debug and hide:
    #     print("hide mode on")
    #     ctypes.windll.user32.ShowWindow(whnd, 0)
    #     ctypes.windll.kernel32.CloseHandle(whnd)
    # else:
    #     print("hide mode off")
    s = socketserver.ThreadingTCPServer((serv, port), goRCServer)
    s.serve_forever()
