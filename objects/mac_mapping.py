import ipaddress
from pydantic import constr, validator

from objects.base import BaseObject
from db.sqlalchemy import api as sqlalchemy_api


class MacMapping(BaseObject):
    id: int = None
    mac_addr: constr(max_length=18) = None
    ipv4_addr: constr(max_length=16) = None
    ipv6_addr: constr(max_length=40) = None

    class Config:
        orm_mode = True

    @validator('ipv4_addr', 'ipv6_addr')
    def validate_ip_addr(cls, ip_addr, field):
        if not ip_addr:
            return ip_addr

        ip = ipaddress.ip_address(ip_addr)
        if field.name == 'ipv4_addr' and ip.version != 4 or \
                field.name == 'ipv6_addr' and ip.version != 6:
            raise ValueError(f"'{ip_addr}' is not a valid {field.name}.")
        return ip_addr

    def create(self):
        if self.obj_field_is_set('id'):
            raise AttributeError(f'{self.mac_addr} already created.')
        mac_mapping = MacMapping.get_by_mac_addr(self.mac_addr)
        if mac_mapping is not None:
            raise ValueError(f'{self.mac_addr} exists.')

        db_mac_mapping = sqlalchemy_api.create_mac_mapping(self)
        self._from_db_object(self, db_mac_mapping)

    @property
    def ip_addr(self):
        return self.ipv4_addr or self.ipv6_addr

    def set_ip_addr(self, ip_addr):
        ip = ipaddress.ip_address(ip_addr)
        if ip.version == 4:
            self.ipv4_addr = ip.compressed
        elif ip.version == 6:
            self.ipv6_addr = ip.compressed

    @classmethod
    def get_by_mac_addr(cls, mac_addr):
        db_mac_mapping = sqlalchemy_api.get_mapping_by_mac_addr(mac_addr)
        if not db_mac_mapping:
            return None

        return MacMapping._from_db_object(cls(mac_addr=mac_addr), db_mac_mapping)

    def save(self):
        if not self.obj_field_is_set('id'):
            raise AttributeError(f'mac_mapping {self.mac_addr} is not exists.')

        updated_value = {}
        for field in self.__fields__:
            updated_value[field] = getattr(self, field)

        sqlalchemy_api.update_mac_mapping(self.id, updated_value)

    def refresh(self):
        latest_db_mac_mapping = sqlalchemy_api.get_mapping_by_mac_addr(self.mac_addr)
        self._from_db_object(self, latest_db_mac_mapping)

    def destroy(self):
        sqlalchemy_api.delete_mac_mapping(self.id)


class MacMappingList(object):
    @classmethod
    def get_all(cls):
        db_mac_mapping_list = sqlalchemy_api.get_all_mac_mapping()
        return cls._make_mac_mapping_list([], db_mac_mapping_list)

    def get_by_filters(self, filters):
        pass

    @staticmethod
    def _make_mac_mapping_list(mac_mappings, db_mac_mapping_list, expected_attrs=None):
        for db_mac_mapping in db_mac_mapping_list:
            mac_mapping = MacMapping._from_db_object(MacMapping(), db_mac_mapping)
            mac_mappings.append(mac_mapping)

        return mac_mappings
