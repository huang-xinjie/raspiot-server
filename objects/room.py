from db.sqlalchemy import api as sqlalchemy_api


class Room(object):
    VERSION = 1.0

    def __init__(self, name, id=None, devices=None, created_at=None, updated_at=None):
        self.id = id
        self.name = name
        self.devices = devices
        self.created_at = created_at
        self.updated_at = updated_at

    @staticmethod
    def _from_db_object(room_inst, db_room_inst, expected_attrs=None):
        for attr in db_room_inst.attrs:
            if expected_attrs is not None \
                    and attr not in expected_attrs:
                continue
            setattr(room_inst, attr, db_room_inst.attr)

    def create(self):
        pass

    @classmethod
    def get_by_id(cls, id):
        db_room = sqlalchemy_api.get_room_by_id()
        return Room._from_db_object(cls(), db_room)

    @classmethod
    def get_by_name(cls, name):
        db_room = sqlalchemy_api.get_room_by_name()
        return Room._from_db_object(cls(), db_room)

    def save(self):
        pass

    def destroy(self):
        pass


class RoomList(object):
    def get_all():
        return []

    def get_by_filters(self, filters):
        pass

    def get_by_name(self, name):
        filters = {'name': name}
        self.get_by_filters(filters)

    @staticmethod
    def _make_room_list(rooms, db_room_list, expected_attrs):
        pass
