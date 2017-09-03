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
        ip = recvdata['ip']
        mac = recvdata['mac']
        module = recvdata['iotServer']
        
        try:
            if os.path.exists('IotServer/' + module + '.py') is False:
                shutil.copyfile('Repository/' + module +'.py', 'IotServer/' + module + '.py')
            exec('from IotServer import ' + module)
            exec('iotServer = ' + module + '.' + module + '("' + ip + '", "'+ mac + '")')
            exec('iotServerList.append(iotServer)')
            conn.sendall(json.dumps({'response':'Setup completed'}).encode())
            #exec('print(iotServerList[0].' + iotServerList[0].buildDeviceJSON()['deviceContent'][0]['getter'] + ')')
        except Exception:
            print('Something error')
