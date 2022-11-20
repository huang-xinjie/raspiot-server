import socket


class SmartFan:
    def __init__(self, device_ip, device_uuid, device_name):
        self.ip = device_ip
        self.uuid = device_uuid
        self.name = device_name
        self.fan_status = False

    def get_fan_status(self):
        self.fan_status = self.connect_with_device('getStatus')
        return self.fan_status

    def set_fan_status(self, value):
        self.fan_status = self.connect_with_device(value)
        return self.fan_status

    def get_device_attribute(self):
        try:
            device = {'uuid': self.uuid,
                      'name': self.name}

            device_content = []
            device_switch = {'type': 'switch',
                             'name': 'Switch',
                             'value': self.get_fan_status(),
                             'setter': 'set_fan_status'}

            device_content.append(device_switch)

            device['deviceContent'] = device_content
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
