import os
import time
import json
import shutil
import socket
import threading

BUFFSIZE = 1024
iotServerList = []


class IotHandlerThread(threading.Thread):
    def __init__(self, conn, recvdata):
        threading.Thread.__init__(self)
        self.conn = conn
        self.recvdata = recvdata

    def run(self):
        self.IotHandler(self.conn, self.recvdata)

    def IotHandler(self, conn, recvdata):
        time.sleep(3)
        ip = recvdata['ip']
        mac = recvdata['mac']
        module = recvdata['iotServer']
        
        try:
            if os.path.exists('IotServer/' + module + '.py') == False:
                shutil.copyfile('Repository/' + module +'.py', 'IotServer/' + module + '.py')
            exec('from IotServer import ' + module)
            exec('iotServer = ' + module + '.' + module + '("' + ip + '", "'+ mac + '")')
            exec('iotServerList.append(iotServer)')
            conn.sendall(json.dumps({'response':'finish'}).encode())
            exec('print(iotServerList[0].' + iotServerList[0].buildDeviceJSON()['deviceContent'][0]['getter'] + ')')
        except Exception:
            print('Something error')
        

if __name__ == '__main__':
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)   
    s.bind(("0.0.0.0",23333))
    s.listen(5)
    while True:
        conn, addr = s.accept()
        print("connected by ", addr)
        recvjson = conn.recv(BUFFSIZE).decode()
        recvdata = json.loads(recvjson)
        print(recvdata)
        IotHandlerThread(conn, recvdata).start()
    s.close()