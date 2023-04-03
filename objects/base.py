import uuid
from datetime import datetime
from pydantic import BaseModel


class BaseObject(BaseModel):
    created_at: datetime = None
    updated_at: datetime = None
    deleted_at: datetime = None

    @property
    def obj_name(self):
        return self.__name__

    @classmethod
    def _from_db_object(cls, obj_inst, db_inst, expected_attrs=None):
        if not db_inst:
            return obj_inst

        db_inst_dict = db_inst.__dict__
        for field in list(db_inst_dict.keys()):
            if field not in cls.__fields__:
                db_inst_dict.pop(field, None)

        obj_inst.update(db_inst_dict)

        return obj_inst

    def _to_db_object(self):
        pass

    def obj_field_is_set(self, field_name):
        if field_name not in self.__fields__:
            raise AttributeError('%(cls_name)s object has no attribute %(field_name)s' %
                                 {'cls_name': self.__class__, 'field_name': field_name})

        value = getattr(self, field_name)
        return value != self.__fields__.get(field_name).default

    @staticmethod
    def generate_uuid(key_word):
        return str(uuid.uuid3(uuid.NAMESPACE_DNS, key_word))

    def get(self, key, default=None):
        if not hasattr(self, key):
            raise AttributeError('%(cls_name)s object has no attribute %(field_name)s' %
                                 {'cls_name': self.__class__, 'field_name': key})
        else:
            return getattr(self, key, default)

    def update(self, updated_dict=None, **kwargs):
        updated_dict = updated_dict or {}
        for filed, value in {**updated_dict, **kwargs}.items():
            if filed in self.__fields__:
                setattr(self, filed, value)
