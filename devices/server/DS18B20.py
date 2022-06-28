import socket


class DS18B20:
    def __init__(self, device_ip, device_uuid, device_name):
        self.ip = device_ip
        self.uuid = device_uuid
        self.name = device_name
        self.temperature = ''

    def get_temp(self):
        self.temperature = self.connect_with_device('get_temp')
        return self.temperature

    def get_device_attribute(self):
        try:
            device = {'uuid': self.uuid, 'name': self.name}

            deviceContent = []
            deviceContent1 = {'type': 'text', 'name': 'Temperature', 'value': self.get_temp()}

            deviceContent.append(deviceContent1)

            device['deviceContent'] = deviceContent
            return device
        except Exception:
            return None

    def connect_with_device(self, cmd):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.ip, 8085))
        s.sendall(cmd.encode())
        recvdata = s.recv(1024).decode()
        s.close()
        return recvdata
