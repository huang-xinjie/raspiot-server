from typing import List

from objects import base
from db.sqlalchemy.models import RoleEnum
from db.sqlalchemy import api as sqlalchemy_api


@base.ObjectRegistry.register
class Role(base.BaseObject):
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
            raise AttributeError(f'{self.name} already created')
        role = Role.get_by_name(self.name)
        if role is not None:
            raise ValueError(f'{self.name} exists')

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
            raise AttributeError(f'role {self.name} is not exists')

        sqlalchemy_api.update_role(self.id, self.obj_what_changes)

    def refresh(self):
        latest_db_role = sqlalchemy_api.get_role_by_name(self.name)
        self._from_db_object(self, latest_db_role)

    def destroy(self):
        sqlalchemy_api.delete_role(self.id)


@base.ObjectRegistry.register
class RoleList(base.BaseObjectList):
    objects: List[Role] = []

    @classmethod
    def get_all(cls):
        db_role_list = sqlalchemy_api.get_all_role()
        return cls._make_list(cls(), db_role_list)

    def get_by_filters(self, filters):
        pass
