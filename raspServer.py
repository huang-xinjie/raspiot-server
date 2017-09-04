import json
import socket  
from CmdParser import cmdParser
from IotManager import IotManager
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
        except KeyError:
            print('Key: identity, not found')
        except Exception as reason:
            print('Error: ' + str(reason))
    s.close()