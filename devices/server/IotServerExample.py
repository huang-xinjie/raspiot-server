import socket


class IotServerExample:
    switchStatus = False

    def __init__(self, deviceIp, deviceUuid, deviceName):
        self.ip = deviceIp
        self.uuid = deviceUuid
        self.name = deviceName

    def get_switch_status(self):
        self.switchStatus = False
        return self.switchStatus

    def set_switch_status(self, value):
        self.switchStatus = value
        return self.switchStatus

    def get_device_attribute(self):
        try:
            device = {'uuid': self.uuid,
                      'name': self.name}

            device_content = []
            device_content_text = {'type': 'text',
                                   'name': 'Text Name',
                                   'value': 'Value'}

            device_content_switch = {'type': 'switch',
                                     'name': 'Switch Name',
                                     'value': self.get_switch_status(),
                                     'setter': 'set_switch_status'}

            device_content_image = {'type': 'image',
                                    'name': 'Image Name',
                                    'value': 'http://www.raspiot.org/static/images/raspIot.jpg'}

            device_content.append(device_content_text)
            device_content.append(device_content_switch)
            device_content.append(device_content_image)

            device['deviceContent'] = device_content
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
