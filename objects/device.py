import ipaddress
import json
import re
from datetime import datetime
from typing import List

from pydantic import validator, constr

from db.sqlalchemy import api as sqlalchemy_api
from db.sqlalchemy.models import DeviceStatus, DeviceProtocol, DeviceAttrType, DeviceSyncMode
from objects.base import BaseObject


class DeviceAttr(BaseObject):
    name: constr(max_length=64) = None
    type: DeviceAttrType = None
    value: constr(max_length=255) = None
    read_only: bool = False
    value_constraint: constr(max_length=255) = None

    @classmethod
    def _from_db_object(cls, obj_inst, db_inst, expected_attrs=None):
        obj_inst = super()._from_db_object(obj_inst, db_inst, expected_attrs)
        obj_inst.value_constraint = json.loads(obj_inst.value_constraint)
        return obj_inst


class Device(BaseObject):
    id: int = None
    uuid: constr(max_length=36) = None
    name: constr(max_length=64) = None

    mac_addr: constr(max_length=18) = None
    ipv4_addr: constr(max_length=16) = None
    ipv6_addr: constr(max_length=40) = None
    protocol: DeviceProtocol = None
    port: int = None

    status: DeviceStatus = DeviceStatus.offline
    sync_mode: DeviceSyncMode = DeviceSyncMode.poll
    report_interval: int = 60 * 5
    reported_at: datetime = None

    attrs: List = []

    class Config:
        orm_mode = True
        validate_assignment = True

    @validator('mac_addr')
    def validate_mac_addr(cls, mac_addr):
        if not (mac_addr and re.match("[0-9a-f]{2}([-:])[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$", mac_addr.lower())):
            raise ValueError(f"'{mac_addr}' is not a valid mac_addr.")

        mac_addr = mac_addr.replace('-', ':')
        return mac_addr.lower()

    @validator('ipv4_addr', 'ipv6_addr')
    def validate_ip_addr(cls, ip_addr, field):
        if not ip_addr:
            return ip_addr

        ip = ipaddress.ip_address(ip_addr)
        if field.name == 'ipv4_addr' and ip.version != 4 or \
                field.name == 'ipv6_addr' and ip.version != 6:
            raise ValueError(f"'{ip_addr}' is not a valid {field.name}.")
        return ip_addr

    @classmethod
    def _from_db_object(cls, obj_inst, db_inst, expected_attrs=None):
        obj_inst = super()._from_db_object(obj_inst, db_inst, expected_attrs)
        obj_inst.attrs = [DeviceAttr._from_db_object(DeviceAttr(), attr)
                          for attr in obj_inst.get('attrs', [])]
        obj_inst.obj_what_changes.clear()
        return obj_inst

    def create(self):
        if self.obj_field_is_set('id'):
            raise AttributeError(f'device with id({self.id}) already created.')
        device = Device.get_by_mac_addr(self.mac_addr)
        if device is not None:
            raise AttributeError(f'{self.name} exists.')

        db_device = sqlalchemy_api.create_device(self)
        self._from_db_object(self, db_device)

    @classmethod
    def get_by_uuid(cls, device_uuid):
        db_device = sqlalchemy_api.get_device_by_uuid(device_uuid)
        if not db_device:
            return None

        return Device._from_db_object(cls(), db_device)

    @classmethod
    def get_by_mac_addr(cls, mac_addr):
        db_device = sqlalchemy_api.get_device_by_mac_addr(mac_addr)
        if not db_device:
            return None
        return Device._from_db_object(cls(), db_device)

    @property
    def addr(self):
        if self.protocol == DeviceProtocol.ble:
            return self.mac_addr, self.port
        return self.ipv4_addr or self.ipv6_addr, self.port

    @property
    def is_online(self):
        return bool(self.status == DeviceStatus.online)

    @property
    def is_poll_mode(self):
        return self.sync_mode == DeviceSyncMode.poll

    def set_ip_addr(self, ip_addr):
        ip = ipaddress.ip_address(ip_addr)
        if ip.version == 4:
            self.ipv4_addr = ip.compressed
        elif ip.version == 6:
            self.ipv6_addr = ip.compressed

    def move_to(self, room):
        sqlalchemy_api.update_device(self.uuid, {'room_id': room.id})

    def online(self):
        if self.status == DeviceStatus.online:
            return

        self.status = DeviceStatus.online
        sqlalchemy_api.update_device(self.uuid, {'status': DeviceStatus.online,
                                                 'reported_at': datetime.now()})

    def offline(self):
        if self.status == DeviceStatus.offline:
            return

        self.status = DeviceStatus.offline
        sqlalchemy_api.update_device(self.uuid, {'status': DeviceStatus.offline})

    def save(self):
        sqlalchemy_api.update_device(self.uuid, self.obj_what_changes)
        self.obj_what_changes.clear()

    def destroy(self):
        sqlalchemy_api.delete_device(self.id)


class DeviceList:
    @classmethod
    def get_by_filters(cls, filters):
        db_devices = sqlalchemy_api.get_devices_by_filters(filters)
        return cls._make_device_list([], db_devices)

    @classmethod
    def get_all(cls):
        db_device_list = sqlalchemy_api.get_all_device()
        return cls._make_device_list([], db_device_list)

    def get_by_name(self, name):
        filters = {'name': name}
        self.get_by_filters(filters)

    @staticmethod
    def _make_device_list(devices, db_device_list, expected_attrs=None):
        for db_device in db_device_list:
            device = Device._from_db_object(Device(), db_device, expected_attrs)
            devices.append(device)

        return devices
