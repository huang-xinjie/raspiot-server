import json
import socket
import requests
from requests import exceptions as req_exc

from log import log
from common import exception


class DeviceDriver(object):
    def __init__(self, timeout=5):
        self.timeout = timeout

    def get_device_details(self, device):
        raise NotImplementedError

    def set_device_detail(self, device, detail, value):
        raise NotImplementedError


class HttpDeviceDriver(DeviceDriver):
    def get_device_details(self, device):
        device_addr = ':'.join(map(str, device.addr))
        device_endpoint = f'http://{device_addr}/details'
        response = requests.get(device_endpoint, timeout=self.timeout)
        log.info(f'Get details from device {device.uuid}: {response.text}')
        return json.loads(response.text)

    def set_device_detail(self, device, detail, value):
        device_addr = ':'.join(map(str, device.addr))
        device_endpoint = f'http://{device_addr}/detail'
        body = {'name': detail, 'value': value}
        headers = {'Content-Length': str(len(str(body)))}
        try:
            response = requests.put(device_endpoint, headers=headers, json=body, timeout=self.timeout)
        except req_exc.ReadTimeout:
            raise exception.DeviceError(f'set device {device.uuid} detail {detail} to {value} timeout={self.timeout}.')
        except Exception as e:
            raise exception.DeviceError(f'set device {device.uuid} detail {detail} to {value} failed: {e}')
        else:
            if response.status_code == 200:
                return json.loads(response.text)


class BleDeviceDriver(DeviceDriver):
    def get_device_details(self, device):
        raise NotImplementedError

    def set_device_detail(self, device, detail, value):
        raise NotImplementedError


class TcpDeviceDriver(DeviceDriver):
    def get_device_details(self, device):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.settimeout(self.timeout)
            client_socket.connect(device.addr)

            body = {'method': 'get',
                    'resource': 'device_details'}
            message = json.dumps(body)
            client_socket.send(message.encode())

            recv_data = client_socket.recv(1024).decode()
            log.info(f'Get details from device {device.uuid}: {recv_data}')
            return json.loads(recv_data)

    def set_device_detail(self, device, detail, value):
        raise NotImplementedError


class UdpDeviceDriver(DeviceDriver):
    def get_device_details(self, device):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client_socket:
            client_socket.settimeout(self.timeout)

            body = {'method': 'get',
                    'resource': 'device_details'}
            message = json.dumps(body)
            client_socket.sendto(message.encode(), device.addr)

            try:
                recv_data, _addr = client_socket.recvfrom(1024)
                log.info(f'Get details from device {device.uuid}: {recv_data.decode()}')
            except socket.timeout:
                log.error(f'Timeout occurred while waiting for device {device.uuid} response')

    def set_device_detail(self, device, detail, value):
        raise NotImplementedError
