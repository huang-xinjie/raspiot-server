import json
import socket
from abc import ABC

import requests
from ping3 import ping
from requests import exceptions as req_exc

from common import exceptions
import log


class DeviceDriver(object):
    protocol = ''

    def __init__(self, timeout=5):
        self.timeout = timeout

    def is_reachable(self, device):
        raise NotImplementedError

    def get_device_attrs(self, device):
        raise NotImplementedError

    def set_device_attr(self, device, attr, value):
        raise NotImplementedError


class HttpDeviceDriver(DeviceDriver):
    protocol = 'http'

    def is_reachable(self, device):
        try:
            response_time = ping(device.addr[0], timeout=1)
            if response_time is not None:
                return True
        except Exception:
            return False

    def get_device_attrs(self, device):
        if not device.is_online and not self.is_reachable(device):
            raise exceptions.DeviceRemoteError(device_uuid=device.uuid, reason=f'device is not reachable')

        device_addr = ':'.join(map(str, device.addr))
        device_endpoint = f'http://{device_addr}/attrs'
        try:
            response = requests.get(device_endpoint, timeout=self.timeout)
            response_text = json.loads(response.text)
            log.info(f'Get attrs from device {device.uuid}: {response_text}')
            return response_text
        except req_exc.ReadTimeout:
            raise exceptions.DeviceConnectTimeout(device_uuid=device.uuid, timeout=self.timeout)
        except req_exc.ConnectionError as e:
            raise exceptions.DeviceRemoteError(device_uuid=device.uuid, reason=f'{e}')

    def set_device_attr(self, device, attr, value):
        if not device.is_online and not self.is_reachable(device):
            raise exceptions.DeviceRemoteError(device_uuid=device.uuid, reason=f'device is not reachable')

        device_addr = ':'.join(map(str, device.addr))
        device_endpoint = f'http://{device_addr}/attr'
        headers = {'Content-Type': 'application/json'}
        body = {'attr': attr, 'value': value}
        try:
            log.info(f'Set device {device.uuid} attrs: {body}')
            response = requests.put(device_endpoint, headers=headers, json=body, timeout=self.timeout)
            if response.status_code != 200:
                raise exceptions.DeviceRemoteError(f'response status code {response.status_code}')
            return json.loads(response.text)
        except req_exc.ReadTimeout:
            raise exceptions.DeviceConnectTimeout(device_uuid=device.uuid, timeout=self.timeout)
        except Exception as e:
            raise exceptions.DeviceRemoteError(f'set device {device.uuid} attr {attr} to {value} failed: {e}')


class BleDeviceDriver(DeviceDriver, ABC):
    protocol = 'ble'

    def get_device_attrs(self, device):
        raise NotImplementedError

    def set_device_attr(self, device, attr, value):
        raise NotImplementedError


class TcpDeviceDriver(DeviceDriver, ABC):
    protocol = 'tcp'

    def get_device_attrs(self, device):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.settimeout(self.timeout)
            client_socket.connect(device.addr)

            body = {'method': 'get',
                    'resource': 'device_attrs'}
            message = json.dumps(body)
            client_socket.send(message.encode())

            recv_data = client_socket.recv(1024).decode()
            log.info(f'Get attrs from device {device.uuid}: {recv_data}')
            return json.loads(recv_data)

    def set_device_attr(self, device, attr, value):
        raise NotImplementedError


class UdpDeviceDriver(DeviceDriver, ABC):
    protocol = 'udp'

    def get_device_attrs(self, device):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client_socket:
            client_socket.settimeout(self.timeout)

            body = {'method': 'get',
                    'resource': 'device_attrs'}
            message = json.dumps(body)
            client_socket.sendto(message.encode(), device.addr)

            try:
                recv_data, _addr = client_socket.recvfrom(1024)
                log.info(f'Get attrs from device {device.uuid}: {recv_data.decode()}')
            except socket.timeout:
                log.error(f'Timeout occurred while waiting for device {device.uuid} response')

    def set_device_attr(self, device, attr, value):
        raise NotImplementedError


def device_driver_factory(device):
    for driver_cls in [HttpDeviceDriver, TcpDeviceDriver, UdpDeviceDriver, BleDeviceDriver]:
        if device.protocol == driver_cls.protocol:
            return driver_cls
    else:
        raise exceptions.InvalidDeviceProtocol(protocol=device.protocol)
