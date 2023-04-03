import re
import uuid
from datetime import datetime
from pydantic import root_validator, validator, constr

from db.sqlalchemy import api as sqlalchemy_api

from objects.base import BaseObject


class Device(BaseObject):
    id: int = None
    uuid: constr(max_length=36) = None
    name: constr(max_length=64) = None
    status: str = None
    mac_addr: constr(max_length=18) = None
    ipv4_addr: constr(max_length=16) = None
    ipv6_addr: constr(max_length=40) = None
    launched_at: datetime = None

    class Config:
        orm_mode = True
        validate_assignment = True

    @validator('mac_addr')
    def validate_mac_addr(cls, mac_addr):
        if mac_addr is not None and not re.match("[0-9a-f]{2}([-:])[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$", mac_addr.lower()):
            raise ValueError('mac_addr "%s" is invalid.' % mac_addr)

        return mac_addr

    @staticmethod
    def generate_uuid(mac_addr):
        return str(uuid.uuid3(uuid.NAMESPACE_DNS, mac_addr))

    def create(self):
        if self.obj_field_is_set('id'):
            raise AttributeError('device with id(%s) already created.' % self.id)
        device = Device.get_by_mac_addr(self.mac_addr)
        if device is not None:
            raise ValueError('%s exists.' % self.name)

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

    def move_to(self, room_id):
        sqlalchemy_api.update_device(self.uuid, {'room_id': room_id})

    def save(self):
        sqlalchemy_api.update_device(self.uuid, {'name': self.name})

    def destroy(self):
        pass


class DeviceList:
    @classmethod
    def get_by_filters(cls, filters):
        db_device = sqlalchemy_api.get_devices_by_filters({'name': filters.get('name')})
        if not db_device:
            return None
        return DeviceList._from_db_object(cls(), db_device)

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
            device = Device._from_db_object(Device(), db_device)
            devices.append(device)

        return devices
