import sys
import json
import socket
import threading
from Kernel.IotManager import IotManager
from Kernel.GlobalConstant import BUFFSIZE

iotManager = IotManager()
cmdParser = iotManager.getCmdParser()

def relayByCloudServer():
    sc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sc.connect(('www.raspIot.org', 22222))
    response = sc.recv(BUFFSIZE).decode()
    print(response)

    while True:
        recvJson = sc.recv(BUFFSIZE).decode()
        print('From cloud: ', recvJson)
        recvdata = json.loads(recvJson)
        cmdParser.commandParser(sc, recvdata)

if __name__ == '__main__':
    try:
        ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ss.bind(("0.0.0.0", 22015))
        ss.listen(5)
    except OSError:
        print('RaspServer is already started.')
        sys.exit(1)

    threading.Thread(target=relayByCloudServer, args=()).start()
    while True:
        conn, addr = ss.accept()
        print("connected by ", addr)
        recvJson = conn.recv(BUFFSIZE).decode()
        print(recvJson)
        recvdata = json.loads(recvJson)
        cmdParser.commandParser(conn, recvdata)
    ss.close()
