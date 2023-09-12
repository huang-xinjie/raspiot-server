import uuid
from copy import deepcopy
from datetime import datetime
from pydantic import BaseModel


class BaseObject(BaseModel):
    created_at: datetime = None
    updated_at: datetime = None
    deleted_at: datetime = None

    obj_what_changes: dict = {}

    @property
    def obj_name(self):
        return self.__name__

    @classmethod
    def obj_fields(cls):
        return cls.__fields__

    def __setattr__(self, field, value):
        super().__setattr__(field, value)
        self.obj_what_changes[field] = deepcopy(value)

    @classmethod
    def _from_db_object(cls, obj_inst, db_inst, expected_attrs=None):
        if not db_inst:
            return obj_inst

        db_inst_dict = db_inst.__dict__
        for field in list(db_inst_dict.keys()):
            if field not in cls.__fields__ or (
                    expected_attrs and field not in expected_attrs):
                db_inst_dict.pop(field, None)

        obj_inst.update(db_inst_dict)
        obj_inst.obj_what_changes.clear()

        return obj_inst

    def _to_db_object(self):
        pass

    def obj_field_is_set(self, field_name):
        if field_name not in self.__fields__:
            raise AttributeError(f'{self.__class__} object has no attribute {field_name}')

        value = getattr(self, field_name)
        return value != self.__fields__.get(field_name).default

    @staticmethod
    def generate_uuid():
        return str(uuid.uuid4())

    def get(self, key, default=None):
        if key not in self.__fields__:
            raise AttributeError(f'{self.__class__} object has no attribute {key}')
        else:
            return getattr(self, key, default)

    def items(self):
        return self.__dict__.items()

    def update(self, updated_dict=None, **kwargs):
        updated_dict = updated_dict or {}
        for field, value in {**updated_dict, **kwargs}.items():
            if field not in self.__fields__:
                raise AttributeError(f'{self.__class__} object has no attribute {field}')
            elif getattr(self, field) == value:
                continue
            else:
                setattr(self, field, value)
