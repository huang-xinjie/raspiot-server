from typing import List
from pydantic import constr

from objects import base
from objects.device import Device
from db.sqlalchemy import api as sqlalchemy_api


@base.ObjectRegistry.register
class Room(base.BaseObject):
    id: int = None
    name: constr(max_length=64) = None
    user_id: constr(max_length=36) = None
    is_public: bool = True
    devices: List[Device] = []

    class Config:
        orm_mode = True

    @classmethod
    def _from_db_object(cls, obj_inst, db_inst, expected_attrs=None):
        super()._from_db_object(obj_inst, db_inst, expected_attrs)
        if db_inst and db_inst.__dict__.get('devices'):
            obj_inst.devices = [d.name for d in db_inst.devices]

        return obj_inst

    def create(self):
        if self.obj_field_is_set('id'):
            raise AttributeError(f'{self.name} already created')
        room = Room.get_by_name(self.name)
        if room is not None:
            raise ValueError(f'{self.name} exists')

        db_room = sqlalchemy_api.create_room(self)
        self._from_db_object(self, db_room)

    @classmethod
    def get_by_name(cls, name):
        db_room = sqlalchemy_api.get_room_by_name(name)
        if not db_room:
            return None

        return Room._from_db_object(cls(name=name), db_room)

    def save(self):
        if not self.obj_field_is_set('id'):
            raise AttributeError(f'room {self.name} is not exists')

        sqlalchemy_api.update_room(self.id, self.obj_what_changes)

    def refresh(self):
        latest_db_room = sqlalchemy_api.get_room_by_name(self.name)
        self._from_db_object(self, latest_db_room)

    def destroy(self):
        sqlalchemy_api.delete_room(self.id)


@base.ObjectRegistry.register
class RoomList(base.BaseObjectList):
    objects: List[Room] = []

    @classmethod
    def get_all(cls):
        db_room_list = sqlalchemy_api.get_all_room()
        return cls._make_list(cls(), db_room_list)

    def get_by_filters(self, filters):
        pass
