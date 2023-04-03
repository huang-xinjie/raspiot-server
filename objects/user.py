from typing import List
from pydantic import constr

from objects.base import BaseObject
from db.sqlalchemy import api as sqlalchemy_api


class User(BaseObject):
    id: int = None
    uuid: constr(max_length=36) = None
    name: constr(max_length=64) = None
    email: constr(max_length=64) = None
    is_admin: bool = True
    rooms: List[str] = []

    class Config:
        orm_mode = True

    def create(self):
        if self.obj_field_is_set('id'):
            raise AttributeError('%s already created.' % self.id)
        user = User.get_by_name(self.name)
        if user is not None:
            raise ValueError('%s exists.' % self.name)

        db_user = sqlalchemy_api.create_user(self)
        self._from_db_object(self, db_user)

    @classmethod
    def get_by_name(cls, name):
        db_user = sqlalchemy_api.get_user_by_name(name)
        if not db_user:
            return None

        return User._from_db_object(cls(name=name), db_user)

    @classmethod
    def get_by_uuid(cls, user_uuid):
        db_user = sqlalchemy_api.get_user_by_uuid(user_uuid)
        if not db_user:
            return None

        return User._from_db_object(cls(), db_user)

    def save(self):
        if not self.obj_field_is_set('id'):
            raise AttributeError('user %s is not exists.' % self.name)

        updated_value = {}
        for field in self.__fields__:
            updated_value[field] = getattr(self, field)

        sqlalchemy_api.update_user(self.id, updated_value)

    def refresh(self):
        latest_db_user = sqlalchemy_api.get_user_by_name(self.name)
        self._from_db_object(self, latest_db_user)

    def destroy(self):
        pass


class UserList(object):
    @classmethod
    def get_all(cls):
        db_user_list = sqlalchemy_api.get_all_user()
        return cls._make_user_list([], db_user_list)

    def get_by_filters(self, filters):
        pass

    def get_by_name(self, name):
        filters = {'name': name}
        self.get_by_filters(filters)

    @staticmethod
    def _make_user_list(users, db_user_list, expected_attrs=None):
        for db_user in db_user_list:
            user = User._from_db_object(User(), db_user)
            users.append(user)

        return users
