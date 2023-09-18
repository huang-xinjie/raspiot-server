from typing import List
from pydantic import constr, root_validator
from werkzeug.security import generate_password_hash, check_password_hash

from objects.role import Role
from objects.base import BaseObject
from db.sqlalchemy import api as sqlalchemy_api
from db.sqlalchemy.models import RoleEnum


class User(BaseObject):
    id: int = None
    uuid: constr(max_length=36) = None
    name: constr(max_length=64) = None
    email: constr(max_length=64) = None
    password_hash: constr(max_length=128) = None
    role: RoleEnum = RoleEnum.member
    rooms: List[str] = []

    class Config:
        orm_mode = True

    @root_validator(pre=True)
    def validate_fields(cls, values):
        if 'password' in values:
            password_hash = generate_password_hash(values.pop('password'))
            values.update({'password_hash': password_hash})
        return values

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute.')

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=7200):
        pass

    @classmethod
    def _from_db_object(cls, obj_inst, db_inst, expected_attrs=None):
        super()._from_db_object(obj_inst, db_inst, expected_attrs)
        if db_inst and db_inst.__dict__.get('role_id'):
            obj_inst.role = Role.get_by_id(db_inst.role_id)

        return obj_inst

    def create(self):
        if self.obj_field_is_set('id'):
            raise AttributeError(f'{self.name} already created.')
        user = User.get_by_name(self.name)
        if user is not None:
            raise ValueError(f'{self.name} exists.')
        role = Role.get_by_name(self.role)
        if not role:
            raise ValueError(f'role {self.role} is not exists.')

        values = {**self.dict(), **{'role_id': role.id}}
        db_user = sqlalchemy_api.create_user(values)
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
            raise AttributeError(f'user {self.name} is not exists.')

        updated_value = {}
        for field in self.__fields__:
            updated_value[field] = getattr(self, field)

        sqlalchemy_api.update_user(self.id, updated_value)

    def refresh(self):
        latest_db_user = sqlalchemy_api.get_user_by_name(self.name)
        self._from_db_object(self, latest_db_user)

    def destroy(self):
        sqlalchemy_api.delete_user(self.id)


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
