import sys
import json
import socket
import threading
from Kernel.IotManager import IotManager
from Kernel.GlobalConstant import BUFFSIZE
from UserConfig import CLOUD_SERVER_ADDRESS
from UserConfig import IDENTITY

iotManager = IotManager()
cmdParser = iotManager.getCmdParser()

def relayByCloudServer():
    # for CloudServer authorized
    RaspServerIdentityJson = json.dumps({'identity': IDENTITY})
    sc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sc.connect(CLOUD_SERVER_ADDRESS)
        sc.sendall(RaspServerIdentityJson.encode())
        print('Connect cloud server finished.')
    except ConnectionRefusedError:
        print('**************************************')
        print('* Error: Cloud server refused.       *')
        print('*        Please check cloud server.  *')
        print('**************************************')
        return  # cloud service disable.
    except TimeoutError:
        print('****************************************************')
        print('* Error: Connect cloud server timeout.             *')
        print('*        Please check network or the cloud server. *')
        print('****************************************************')
        return  # cloud service disable.
    while True:
        recvJson = sc.recv(BUFFSIZE).decode()
        if recvJson == 'Connect finished.' or recvJson == '':
            continue
        elif recvJson == 'Heartbeat detection.':
            sc.sendall('Roger.'.encode())
            continue
        elif recvJson == 'You need to log in.':
            print('From raspCloud: ', recvJson)
            return
        print('From cloud: ', recvJson)
        try:
            recvdata = json.loads(recvJson)
            cmdParser.commandParser(sc, recvdata)
        except Exception:
            sc.sendall('Invalid json!'.encode())
            sc.close()
        sc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sc.connect(('www.raspIot.org', 22222))
        sc.sendall(RaspServerIdentityJson.encode())

if __name__ == '__main__':
    try:
        ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ss.bind(("0.0.0.0", 22015))
        ss.listen(5)
    except OSError:
        print('raspServer has started, please check.')
        sys.exit(1)

    print('raspServer is running.')
    threading.Thread(target=relayByCloudServer, args=()).start()
    while True:
        conn, addr = ss.accept()
        print("connected by ", addr)
        recvJson = conn.recv(BUFFSIZE).decode()
        print(recvJson)
        recvdata = json.loads(recvJson)
        cmdParser.commandParser(conn, recvdata)
    ss.close()
