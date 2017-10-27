import socket

class IotServerExample:
    switchStatus = ''

    def __init__(self, deviceIp, deviceUuid, deviceName):
        self.ip = deviceIp
        self.uuid = deviceUuid
        self.name = deviceName

    def getSwitchStatus(self):
        self.switchStatus = False
        return self.switchStatus

    def setSwitchStatus(self, value):
        self.switchStatus = value
        return self.switchStatus


    def getDeviceAttribute(self):
        try:
            device = {}
            device['uuid'] = self.uuid
            device['name'] = self.name

            deviceContent = []
            deviceContent0 = {}
            deviceContent0['type'] = 'text'
            deviceContent0['name'] = 'Text Name'
            deviceContent0['value'] = 'Value'

            deviceContent1 = {}
            deviceContent1['type'] = 'switch'
            deviceContent1['name'] = 'Switch Name'
            deviceContent1['value'] = self.getSwitchStatus()
            deviceContent1['setter'] = 'setSwitchStatus'

            deviceContent2 = {}
            deviceContent2['type'] = 'image'
            deviceContent2['name'] = 'Image Name'
            deviceContent2['value'] = 'http://www.raspiot.org/static/images/raspIot.jpg'

            deviceContent.append(deviceContent0)
            deviceContent.append(deviceContent1)
            deviceContent.append(deviceContent2)


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
