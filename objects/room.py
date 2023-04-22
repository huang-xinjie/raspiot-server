from typing import List
from pydantic import constr

from objects.base import BaseObject
from db.sqlalchemy import api as sqlalchemy_api


class Room(BaseObject):
    id: int = None
    name: constr(max_length=64) = None
    user_id: constr(max_length=36) = None
    is_public: bool = True
    devices: List[str] = []

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
            raise AttributeError('%s already created.' % self.name)
        room = Room.get_by_name(self.name)
        if room is not None:
            raise ValueError('%s exists.' % self.name)

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
            raise AttributeError('room %s is not exists.' % self.name)

        updated_value = {}
        for field in self.__fields__:
            updated_value[field] = getattr(self, field)

        sqlalchemy_api.update_room(self.id, updated_value)

    def refresh(self):
        latest_db_room = sqlalchemy_api.get_room_by_name(self.name)
        self._from_db_object(self, latest_db_room)

    def destroy(self):
        sqlalchemy_api.delete_room(self.id)


class RoomList(object):
    @classmethod
    def get_all(cls):
        db_room_list = sqlalchemy_api.get_all_room()
        return cls._make_room_list([], db_room_list)

    def get_by_filters(self, filters):
        pass

    def get_by_name(self, name):
        filters = {'name': name}
        self.get_by_filters(filters)

    @staticmethod
    def _make_room_list(rooms, db_room_list, expected_attrs=None):
        for db_room in db_room_list:
            room = Room._from_db_object(Room(), db_room)
            rooms.append(room)

        return rooms
