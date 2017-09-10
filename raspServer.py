import sys
import json
import socket
from Kernel.IotManager import IotManager
from Kernel.GlobalConstant import BUFFSIZE

if __name__ == '__main__':
    iotManager = IotManager()
    cmdParser = iotManager.getCmdParser()
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(("0.0.0.0", 22015))
        s.listen(5)
    except OSError:
        print('RaspServer is already started.')
        sys.exit(1)

    while True:
        conn, addr = s.accept()
        print("connected by ", addr)
        recvJson = conn.recv(BUFFSIZE).decode()
        print(recvJson)
        try:
            recvdata = json.loads(recvJson)
            cmdParser.commandParser(conn, recvdata)
        except Exception as reason:
            print(__file__ +' Error: ' + str(reason))
    s.close()
