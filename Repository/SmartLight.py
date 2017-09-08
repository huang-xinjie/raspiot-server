import socket

class SmartLight:
    lightStatus = ''

    def __init__(self, deviceIp, deviceUuid):
        self.ip = deviceIp
        self.uuid = deviceUuid

    def getLightStatus(self):
        self.lightStatus = self.connectWithDevice('getStatus')
        return self.lightStatus

    def setLightStatus(self, value):
        self.lightStatus = self.connectWithDevice(value)
        return self.lightStatus


    def getDeviceAttribute(self):
        device = {}
        device['uuid'] = self.uuid
        device['name'] = 'Smart light'

        deviceContent = []
        deviceContent1 = {}
        deviceContent1['type'] = 'switch'
        deviceContent1['name'] = '开关'
        deviceContent1['value'] = self.getLightStatus()
        deviceContent1['setter'] = 'setLightStatus'

        deviceContent.append(deviceContent1)

        device['deviceContent'] = deviceContent

        return device

    def connectWithDevice(self, cmd):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.ip, 8085))
        s.sendall(cmd.encode())
        recvdata = s.recv(1024).decode()
        s.close()
        return recvdata