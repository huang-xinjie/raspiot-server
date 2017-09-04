import json
import socket  
from CmdParser import cmdParser
from IoTManager import IotManager
from GlobalConstant import BUFFSIZE

if __name__ == '__main__':
    iotManager = IotManager()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("0.0.0.0", 22223))
    s.listen(5)

    while True:
        conn, addr = s.accept()
        print("connected by ", addr)
        recvJson = conn.recv(BUFFSIZE).decode()
        print(recvJson)
        try:
            recvdata = json.loads(recvJson)
            if recvdata['identity'] == 'app':
                cmdParser(conn, recvdata)
            elif recvdata['identity'] == 'device':
                iotManager.setupIotServer(conn, recvdata)
        except Exception:
            pass
    s.close()