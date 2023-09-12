import time
import socket
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

import schedule
from scapy.layers.l2 import ARP
from scapy.layers.l2 import Ether
from scapy.sendrecv import srp

from api import service
from common import exceptions, utils
from iot.device.driver import device_driver_factory
import log
from objects.device import Device, DeviceList
from objects.mac_mapping import MacMapping, MacMappingList


class DeviceManager:
    def __init__(self, manager_pipe=None, broadcast_run=True):
        self.manager_pipe = manager_pipe
        self.tracked_devices = set()
        self.lan_mac_mapping = {}
        self.db_app = None
        self.init_with_db()

        self.broadcast_run = broadcast_run
        self.thread_pool = ThreadPoolExecutor(max_workers=5)

    def init_with_db(self):
        self.db_app = service.create(register_all=False)
        with self.db_app.app_context():
            devices = DeviceList.get_all()
            mac_mappings = MacMappingList.get_all()

        for device in devices:
            self.tracked_devices.add(device.uuid)

        for mapping in mac_mappings:
            self.lan_mac_mapping[mapping.mac_addr] = mapping.ip_addr

    @property
    def _lan_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
            return ip
        finally:
            s.close()

    def init_periodic_tasks(self):
        schedule.every(60).seconds.do(self.arp_broadcast)
        schedule.every(300).seconds.do(self.poll_devices)

        schedule.run_all()

    def run_periodic_tasks(self):
        self.init_periodic_tasks()

        while True:
            schedule.run_pending()
            time.sleep(1)

    def run(self):
        self.thread_pool.submit(self.run_periodic_tasks)

        while self.manager_pipe:
            method_name, args, kwargs = self.manager_pipe.recv()
            self.call_method_from_pipe(method_name, *args, **kwargs)

    def arp_broadcast(self, timeout=5, verbose=False):
        if not self.broadcast_run:
            return

        arp_request = Ether(dst='ff:ff:ff:ff:ff:ff') / ARP(op=1, pdst=f'{self._lan_ip}/24')
        reply = srp(arp_request, timeout=timeout, verbose=verbose)[0]
        latest_lan_mac_ip_mapping = {recv.hwsrc: recv.psrc for send, recv in reply}
        for mac_addr, ip_addr in latest_lan_mac_ip_mapping.items():
            with self.db_app.app_context():
                if mac_addr not in self.lan_mac_mapping:
                    mac_mapping = MacMapping(mac_addr=mac_addr)
                    mac_mapping.set_ip_addr(ip_addr)
                    mac_mapping.create()
                    self.lan_mac_mapping.update({mac_addr: mac_mapping.ip_addr})
                elif ip_addr != self.lan_mac_mapping[mac_addr]:
                    mac_mapping = self.lan_mac_mapping.get(mac_addr)
                    mac_mapping.set_ip_addr(ip_addr)
                    mac_mapping.save()
                    self.lan_mac_mapping.update({mac_addr: mac_mapping.ip_addr})

    def poll_devices(self):
        def offline_when_report_attrs_timeout(device):
            if device.is_online and utils.is_exceeded(device.reported_at, device.report_interval):
                log.error(f'device {device.uuid} report attrs at {device.reported_at}, '
                          f'exceed report interval ({device.report_interval}), set it offline.')
                device.offline()

        def _poll_device_with_context():
            for uuid in self.tracked_devices:
                device = Device.get_by_uuid(uuid)
                if not device:
                    log.warning(f'device {uuid} not found, remove from tracked_devices.')
                    self.tracked_devices.remove(uuid)
                    continue

                try:
                    if device.is_poll_mode:
                        attrs = self.get_device_attrs(device)
                        device.update(attrs=attrs, reported_at=datetime.now())
                        device.online()
                        device.save()
                except exceptions.DeviceBasicAttributeError:
                    log.error(f'device {uuid} ip address is empty.')
                    device.offline()
                except exceptions.DeviceConnectTimeout:
                    if device.is_online:
                        log.error(f'connect device {uuid} timeout, set it offline.')
                        device.offline()
                except exceptions.DeviceRemoteError as e:
                    if device.is_online:
                        log.error(f'poll device {uuid} attrs failed: {e}')
                        device.offline()
                except Exception as e:
                    log.exception(f'poll device {uuid} attrs failed: {e}')
                finally:
                    offline_when_report_attrs_timeout(device)

        with self.db_app.app_context():
            _poll_device_with_context()

    def call_method_from_pipe(self, method_name, *args, **kwargs):
        try:
            method = getattr(self, method_name)
            self.manager_pipe.send(method(*args))
        except Exception as e:
            log.error(f'call method {method_name} failed: {e}')
            self.manager_pipe.send(e)

    def get_ip_by_mac_addr(self, mac_addr):
        return self.lan_mac_mapping.get(mac_addr)

    def get_device_attrs(self, device, timeout=5):
        if device.uuid not in self.tracked_devices:
            self.tracked_devices.add(device.uuid)

        if not device.addr[0]:
            ip_addr = self.get_ip_by_mac_addr(device.mac_addr)
            if not ip_addr:
                raise exceptions.DeviceBasicAttributeError(device_uuid=device.uuid, attribute='ipv4_addr/ipv6_addr')
            device.set_ip_addr(ip_addr)

        driver = device_driver_factory(device)(timeout=timeout)
        attrs = driver.get_device_attrs(device)
        return attrs

    def set_device_attr(self, device, attr, value):
        if not device.addr[0]:
            ip_addr = self.get_ip_by_mac_addr(device.mac_addr)
            if not ip_addr:
                raise exceptions.DeviceBasicAttributeError(device_uuid=device.uuid, attribute='ipv4_addr/ipv6_addr')
            device.set_ip_addr(ip_addr)

        driver = device_driver_factory(device)()
        attrs = driver.set_device_attr(device, attr, value)
        return attrs
