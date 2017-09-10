import socket

class IotServer:

    def __init__(self, deviceIp, deviceUuid):
        self.ip = deviceIp
        self.uuid = deviceUuid

    def getDeviceAttribute(self):
        device = {}
        device['uuid'] = self.uuid
        device['name'] = 'device name'

        deviceContent = []
        deviceContent1 = {}
        deviceContent1['type'] = 'switch'
        deviceContent1['name'] = 'Switch Name'
        deviceContent1['value'] = 'false'
        deviceContent1['setter'] = 'getValue'
        
        device['deviceContent'] = deviceContent

        return device

    def connectWithDevice(self, cmd):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.ip, 8085))
        s.sendall(cmd.encode())
        recvdata = s.recv(1024).decode()
        s.close()
        return recvdata