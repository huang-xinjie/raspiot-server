import threading


def rpc_device_manager_with_pipe(rpc_method):
    def wrapped(self, *args, **kwargs):
        with self.pipe_lock:
            self.server_pipe.send((rpc_method.__name__, args, kwargs))
            recv_data = self.server_pipe.recv()
            if isinstance(recv_data, Exception):
                raise recv_data
            return recv_data

    return wrapped


class DeviceManagerApi:
    def __init__(self, server_pipe):
        self.pipe_lock = threading.Lock()
        self.server_pipe = server_pipe

    @rpc_device_manager_with_pipe
    def get_ip_by_mac_addr(self, mac_addr):
        """get device ip by mac address"""

    @rpc_device_manager_with_pipe
    def get_device_attrs(self, device):
        """get device attrs from iot device"""

    @rpc_device_manager_with_pipe
    def set_device_attr(self, device, attr, value):
        """set device attrs to iot device"""
