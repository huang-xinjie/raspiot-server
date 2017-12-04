import time
import socket
import threading

class SafeKeeper:
    picUrl = None

    def __init__(self, deviceIp, deviceUuid, deviceName):
        self.ip = deviceIp
        self.uuid = deviceUuid
        self.name = deviceName
        threading.Thread(target=self.connectWithDevice, args=()).start()

    def getDeviceAttribute(self):
        try:
            device = {}
            device['uuid'] = self.uuid
            device['name'] = self.name

            deviceContent = []
            deviceContent0 = {}
            deviceContent0['type'] = 'text'
            deviceContent0['name'] = 'Safe Door'
            deviceContent0['value'] = 'Close'
            if SafeKeeper.picUrl:
                deviceContent0['value'] = 'Open'

            deviceContent.append(deviceContent0)

            if SafeKeeper.picUrl:
                deviceContent1 = {}
                deviceContent1['type'] = 'image'
                deviceContent1['name'] = 'Current pic'
                deviceContent1['value'] = SafeKeeper.picUrl
                deviceContent.append(deviceContent1)

            device['deviceContent'] = deviceContent
            return device
        except Exception:
            return None

    def connectWithDevice(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect((self.ip, 18085))
            s.sendall('SafeKeeper'.encode())
            s.sendall('getUrl'.encode())
            recvdata = s.recv(1024).decode()
            if recvdata != 'NULL':
                SafeKeeper.picUrl = recvdata.decode()
            else:
                SafeKeeper.picUrl = None
        finally:
            s.close()