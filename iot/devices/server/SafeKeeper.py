import time
import socket
import threading


class SafeKeeper:
    def __init__(self, deviceIp, deviceUuid, deviceName):
        self.ip = deviceIp
        self.uuid = deviceUuid
        self.name = deviceName
        self.pic_url = None

    def get_pic_url(self):
        self.connect_with_device()

    def get_device_attribute(self):
        try:
            self.get_pic_url()
            device = {'uuid': self.uuid,
                      'name': self.name}

            deviceContent = []
            deviceContent0 = {'type': 'text',
                              'name': 'Safe Door',
                              'value': 'Close'}
            if self.pic_url:
                deviceContent0['value'] = 'Open'

            deviceContent.append(deviceContent0)

            if self.pic_url:
                deviceContent1 = {'type': 'image',
                                  'name': 'Current pic',
                                  'value': self.pic_url}
                deviceContent.append(deviceContent1)

            device['deviceContent'] = deviceContent
            return device
        except Exception as reason:
            print(self.__class__.__name__ + ' Error: ' + str(reason))
            return None

    def connect_with_device(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)
        try:
            s.connect((self.ip, 18085))
            s.sendall('SafeKeeper'.encode())
            s.sendall('getUrl'.encode())
            recvdata = s.recv(1024).decode()
            if recvdata != 'NULL':
                SafeKeeper.picUrl = recvdata
            else:
                SafeKeeper.picUrl = None
        finally:
            s.close()
