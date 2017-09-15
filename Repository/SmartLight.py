import socket

class SmartLight:
    lightStatus = ''

    def __init__(self, deviceIp, deviceUuid, deviceName):
        self.ip = deviceIp
        self.uuid = deviceUuid
        self.name = deviceName

    def getLightStatus(self):
        self.lightStatus = self.connectWithDevice('getStatus')
        return self.lightStatus

    def setLightStatus(self, value):
        self.lightStatus = self.connectWithDevice(value)
        return self.lightStatus


    def getDeviceAttribute(self):
        try:
            device = {}
            device['uuid'] = self.uuid
            device['name'] = self.name

            deviceContent = []
            deviceContent1 = {}
            deviceContent1['type'] = 'switch'
            deviceContent1['name'] = 'Switch'
            deviceContent1['value'] = self.getLightStatus()
            deviceContent1['setter'] = 'setLightStatus'

            deviceContent.append(deviceContent1)

            device['deviceContent'] = deviceContent
            return device
        except Exception:
            return None

    def connectWithDevice(self, cmd):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.ip, 8085))
        s.sendall(cmd.encode())
        recvdata = s.recv(1024).decode()
        s.close()
        return recvdata
