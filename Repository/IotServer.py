import socket

class IotServer:

    def __init__(self, deviceIp, deviceUuid, deviceName):
        self.ip = deviceIp
        self.uuid = deviceUuid
        self.name = deviceName

    def getDeviceAttribute(self):
        try:
            device = {}
            device['uuid'] = self.uuid
            device['name'] = self.name

            deviceContent = []
            deviceContent1 = {}
            deviceContent1['type'] = 'switch'
            deviceContent1['name'] = 'Switch Name'
            deviceContent1['value'] = 'false'
            deviceContent1['setter'] = 'getValue'

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