from typing import List

from objects.base import BaseObject
from db.sqlalchemy.models import RoleEnum
from db.sqlalchemy import api as sqlalchemy_api


class Role(BaseObject):
    id: int = None
    name: RoleEnum = None
    users: List[str] = []

    class Config:
        orm_mode = True

    @classmethod
    def _from_db_object(cls, obj_inst, db_inst, expected_attrs=None):
        super()._from_db_object(obj_inst, db_inst, expected_attrs)
        if db_inst and db_inst.__dict__.get('users'):
            obj_inst.users = [u.uuid for u in db_inst.users]

        return obj_inst

    def create(self):
        if self.obj_field_is_set('id'):
            raise AttributeError('%s already created.' % self.name)
        role = Role.get_by_name(self.name)
        if role is not None:
            raise ValueError('%s exists.' % self.name)

        db_role = sqlalchemy_api.create_role(self)
        self._from_db_object(self, db_role)

    @classmethod
    def get_by_name(cls, name):
        db_role = sqlalchemy_api.get_role_by_name(name)
        if not db_role:
            return None

        return Role._from_db_object(cls(name=name), db_role)

    @classmethod
    def get_by_id(cls, role_id):
        db_role = sqlalchemy_api.get_role_by_id(role_id)
        if not db_role:
            return None

        return Role._from_db_object(cls(), db_role)

    def save(self):
        if not self.obj_field_is_set('id'):
            raise AttributeError('role %s is not exists.' % self.name)

        updated_value = {}
        for field in self.__fields__:
            updated_value[field] = getattr(self, field)

        sqlalchemy_api.update_role(self.id, updated_value)

    def refresh(self):
        latest_db_role = sqlalchemy_api.get_role_by_name(self.name)
        self._from_db_object(self, latest_db_role)

    def destroy(self):
        sqlalchemy_api.delete_role(self.id)


class RoleList(object):
    @classmethod
    def get_all(cls):
        db_role_list = sqlalchemy_api.get_all_role()
        return cls._make_role_list([], db_role_list)

    def get_by_filters(self, filters):
        pass

    def get_by_name(self, name):
        filters = {'name': name}
        self.get_by_filters(filters)

    @staticmethod
    def _make_role_list(roles, db_role_list, expected_attrs=None):
        for db_role in db_role_list:
            role = Role._from_db_object(Role(), db_role)
            roles.append(role)

        return roles
