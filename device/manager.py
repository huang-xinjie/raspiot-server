import ipaddress
import platform
import socket
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

import schedule
from scapy.all import get_if_list, get_if_hwaddr
from scapy.layers.l2 import ARP
from scapy.layers.l2 import Ether
from scapy.sendrecv import srp

import log
from api import service
from common import exceptions, utils
from device.driver import device_driver_factory
from objects.device import Device, DeviceList, DeviceAttrList
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

        if not self.is_linux():
            return

        # for devices which running on same host
        for iff in get_if_list():
            mac_addr = get_if_hwaddr(iff)
            self.lan_mac_mapping[mac_addr] = '127.0.0.1'

    @property
    def _lan_ips(self):
        if self.is_linux():
            ips = subprocess.check_output(['hostname', '-I'])
            return ips.decode().strip().split()
        else:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            try:
                s.connect(('8.8.8.8', 80))
                return [s.getsockname()[0]]
            finally:
                s.close()

    @staticmethod
    def is_linux():
        return platform.system() == "Linux"

    def init_periodic_tasks(self):
        schedule.every(60).seconds.do(self.arp_broadcast).tag('arp_broadcast')
        schedule.every(300).seconds.do(self.sync_devices).tag('sync_devices')

        schedule.run_all()

    def run_periodic_tasks(self):
        last_run = datetime.now()
        self.init_periodic_tasks()

        while True:
            schedule.run_pending()

            for job in schedule.jobs:
                if job.last_run > last_run:
                    log.info(f'run periodic task {", ".join(job.tags)}')
            last_run = max([job.last_run for job in schedule.jobs])
            time.sleep(1)

    def run(self):
        self.thread_pool.submit(self.run_periodic_tasks)

        while self.manager_pipe:
            method_name, args, kwargs = self.manager_pipe.recv()
            self.call_method_from_pipe(method_name, *args, **kwargs)

    @utils.wrap_and_log_exception
    def arp_broadcast(self, timeout=5, verbose=False):
        if not self.broadcast_run:
            return

        latest_lan_mac_ip_mapping = {}
        for lan_ip in self._lan_ips:
            ip = ipaddress.ip_address(lan_ip)
            if ip.version == 4:
                arp_request = Ether(dst='ff:ff:ff:ff:ff:ff') / ARP(op=1, pdst=f'{lan_ip}/24')
                reply = srp(arp_request, timeout=timeout, verbose=verbose)[0]
                latest_lan_mac_ip_mapping.update({recv.hwsrc: recv.psrc for send, recv in reply})
        log.info(f'latest lan mac mappings: {latest_lan_mac_ip_mapping}')
        for mac_addr, ip_addr in latest_lan_mac_ip_mapping.items():
            with self.db_app.app_context():
                if mac_addr not in self.lan_mac_mapping:
                    mac_mapping = MacMapping(mac_addr=mac_addr)
                    mac_mapping.set_ip_addr(ip_addr)
                    mac_mapping.create()
                    self.lan_mac_mapping.update({mac_addr: mac_mapping.ip_addr})
                elif ip_addr != self.lan_mac_mapping[mac_addr]:
                    mac_mapping = MacMapping.get_by_mac_addr(mac_addr)
                    mac_mapping.set_ip_addr(ip_addr)
                    mac_mapping.save()
                    self.lan_mac_mapping.update({mac_addr: mac_mapping.ip_addr})

    @utils.wrap_and_log_exception
    def sync_devices(self):
        def offline_when_sync_attrs_timeout(device):
            if device.uuid in self.tracked_devices and device.is_online and \
                    utils.is_exceeded(device.synced_at, device.sync_interval):
                log.error(f'device {device.uuid} synced attrs at {device.synced_at}, '
                          f'exceed report interval ({device.sync_interval}), set it offline.')
                device.offline()

        def _sync_devices_with_context():
            for uuid in list(self.tracked_devices):
                device = Device.get_by_uuid(uuid)
                if not device:
                    log.warning(f'device {uuid} not found, remove from tracked_devices.')
                    self.tracked_devices.remove(uuid)
                    continue

                try:
                    if device.is_poll_mode:
                        attrs = self.get_device_attrs(device)
                        device.update(attrs=DeviceAttrList.from_primitive(attrs),
                                      synced_at=datetime.now())
                        device.online()
                        device.save()
                except exceptions.DeviceNotFound:
                    log.warning(f'device {uuid} deleted during sync, remove from tracked_devices.')
                    self.tracked_devices.remove(uuid)
                except exceptions.DeviceBasicAttributeError:
                    log.error(f'device {uuid} ip address is empty.')
                    device.offline()
                except exceptions.DeviceConnectTimeout:
                    if device.is_online:
                        log.error(f'connect device {uuid} timeout, set it offline.')
                        device.offline()
                except exceptions.DeviceRemoteError as e:
                    if device.is_online:
                        log.error(f'sync device {uuid} attrs failed: {e}')
                        device.offline()
                except Exception as e:
                    log.exception(f'sync device {uuid} attrs failed: {e}')
                finally:
                    offline_when_sync_attrs_timeout(device)

        with self.db_app.app_context():
            _sync_devices_with_context()

    def call_method_from_pipe(self, method_name, *args, **kwargs):
        try:
            method = getattr(self, method_name)
            self.manager_pipe.send(method(*args, **kwargs))
        except Exception as e:
            log.error(f'call method {method_name} failed: {e}')
            self.manager_pipe.send(e)

    def get_ip_by_mac_addr(self, mac_addr):
        return self.lan_mac_mapping.get(mac_addr)

    def get_device_attrs(self, device, timeout=5):
        if device.uuid not in self.tracked_devices:
            self.tracked_devices.add(device.uuid)

        ip_addr = self.get_ip_by_mac_addr(device.mac_addr)
        if not (device.addr[0] or ip_addr):
            raise exceptions.DeviceBasicAttributeError(device_uuid=device.uuid, attribute='ipv4_addr/ipv6_addr')

        if ip_addr and ip_addr != device.addr[0]:
            device.set_ip_addr(ip_addr)

        driver = device_driver_factory(device)(timeout=timeout)
        attrs = driver.get_device_attrs(device)
        return attrs

    def set_device_attr(self, device, attr, value):
        ip_addr = self.get_ip_by_mac_addr(device.mac_addr)
        if not (device.addr[0] or ip_addr):
            raise exceptions.DeviceBasicAttributeError(device_uuid=device.uuid, attribute='ipv4_addr/ipv6_addr')
        if ip_addr and ip_addr != device.addr[0]:
            device.set_ip_addr(ip_addr)

        driver = device_driver_factory(device)()
        attrs = driver.set_device_attr(device, attr, value)
        return attrs
