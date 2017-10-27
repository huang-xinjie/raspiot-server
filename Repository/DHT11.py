import socket

class DHT11:
    temperature = ''
    humidity = ''

    def __init__(self, deviceIp, deviceUuid, deviceName):
        self.ip = deviceIp
        self.uuid = deviceUuid
        self.name = deviceName

    def getTempAndHumi(self):
        recvdata = self.connectWithDevice('getTemp&Humi')
        self.temperature, self.humidity = recvdata.split('&')

    def getDeviceAttribute(self):
        try:
            self.getTempAndHumi()
        except Exception:
            return None

        device = {}
        device['uuid'] = self.uuid
        device['name'] = self.name

        deviceContent = []
        deviceContent1 = {}
        deviceContent1['type'] = 'text'
        deviceContent1['name'] = 'Temperature'
        deviceContent1['value'] = self.temperature + '℃'

        deviceContent1 = {}
        deviceContent1['type'] = 'text'
        deviceContent1['name'] = 'Humidity'
        deviceContent1['value'] = self.humidity + '%'
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
