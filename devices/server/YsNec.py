import socket
import binascii


class YsNec:
    def __init__(self, device_ip, device_uuid, device_name):
        self.ip = device_ip
        self.uuid = device_uuid
        self.name = device_name
        self.sc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sc.connect((self.ip, 8085))

    def encode(self):
        self.sc.sendall(binascii.b2a_hex(b'A1 F1 A0 F0 CC'))
        response = self.sc.recv(1024).decode()
        if response == 'F1':
            return 'ok'
        else:
            return 'fail'

    def get_device_attribute(self):
        try:
            device = {'uuid': self.uuid, 'name': self.name}

            deviceContent = []
            deviceContent1 = {'type': 'button',
                              'name': 'TV switch',
                              'value': 'ON',
                              'setter': 'encode'}

            deviceContent.append(deviceContent1)

            device['deviceContent'] = deviceContent
            return device
        except Exception:
            return None
