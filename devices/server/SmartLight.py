import socket


class SmartLight:
    def __init__(self, device_ip, device_uuid, device_name):
        self.ip = device_ip
        self.uuid = device_uuid
        self.name = device_name
        self.light_status = False

    def get_light_status(self):
        self.light_status = self.connect_with_device('getStatus')
        return self.light_status

    def set_light_status(self, value):
        self.light_status = self.connect_with_device(value)
        return self.light_status

    def get_device_attribute(self):
        try:
            device = {'uuid': self.uuid, 'name': self.name}

            deviceContent = []
            deviceContent1 = {'type': 'switch',
                              'name': 'Switch',
                              'value': self.get_light_status(),
                              'setter': 'set_light_status'}

            deviceContent.append(deviceContent1)

            device['deviceContent'] = deviceContent
            return device
        except Exception:
            return None

    def connect_with_device(self, cmd):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.ip, 8085))
        s.sendall(cmd.encode())
        recv_data = s.recv(1024).decode()
        s.close()
        return recv_data
