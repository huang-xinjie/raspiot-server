import socket

class DS18B20:
    temperature = ''

    def __init__(self, deviceIp, deviceMac):
        self.ip = deviceIp
        self.mac = deviceMac


    def getTemp(self):
        return self.connectWithDevice('getTemp')


    def buildDeviceJSON(self):
        device = {}
        device['uuid'] = 'MAC'
        device['name'] = 'DS18B20 Temperature sensor'
        
        deviceContent = []
        deviceContent1 = {}
        deviceContent1['type'] = 'text'
        deviceContent1['name'] = 'Temperature'
        deviceContent1['value'] = self.getTemp()
        deviceContent1['getter'] = 'getTemp()'
        
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
