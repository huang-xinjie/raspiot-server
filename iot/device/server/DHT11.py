import socket


class DHT11:
    def __init__(self, deviceIp, deviceUuid, deviceName):
        self.ip = deviceIp
        self.uuid = deviceUuid
        self.name = deviceName
        self.temperature = ''
        self.humidity = ''

    def get_temp_and_humi(self):
        recvdata = self.connect_with_device('get_temp&Humi')
        self.temperature, self.humidity = recvdata.split('&')

    def get_device_attribute(self):
        try:
            self.get_temp_and_humi()
        except Exception:
            return None

        device = {'uuid': self.uuid, 'name': self.name}

        deviceContent = []
        deviceContent1 = {'type': 'text', 'name': 'Temperature', 'value': self.temperature + '℃'}

        deviceContent2 = {'type': 'text', 'name': 'Humidity', 'value': self.humidity + '%'}

        deviceContent.append(deviceContent1)
        deviceContent.append(deviceContent2)
        device['deviceContent'] = deviceContent
        return device

    def connect_with_device(self, cmd):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.ip, 8085))
        s.sendall(cmd.encode())
        recvdata = s.recv(1024).decode()
        s.close()
        return recvdata
