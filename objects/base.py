import uuid
from copy import deepcopy
from datetime import datetime
from typing import List, get_type_hints
from pydantic import BaseModel

import objects
from common import exceptions


class ObjectRegistry(object):
    @staticmethod
    def register_class(obj_cls):
        if getattr(objects, obj_cls.__name__, None):
            raise exceptions.ObjectRegistryConflict(class_name=obj_cls.__name__)
        setattr(objects, obj_cls.__name__, obj_cls)

    @classmethod
    def register(cls, obj_cls):
        cls.register_class(obj_cls)
        return obj_cls


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

    def __getitem__(self, key):
        if key not in self.__fields__:
            raise AttributeError(f'{self.__class__} object has no attribute {key}')
        else:
            return getattr(self, key, None)

    def __setitem__(self, field, value):
        if field not in self.__fields__:
            raise AttributeError(f'{self.__class__} object has no attribute {field}')
        setattr(self, field, value)

    @classmethod
    def obj_class(cls, field):
        obj_type = get_type_hints(cls).get(field)
        return obj_type or object

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

    def to_primitive(self):
        primitive = dict()
        for field, value in self.__dict__.items():
            if self.obj_field_is_set(field):
                if isinstance(value, (BaseObject, BaseObjectList)):
                    value = value.to_primitive()
                primitive[field] = value

        return primitive

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


class BaseObjectList(BaseModel):
    objects: List[BaseObject] = []

    def __getitem__(self, index):
        """List index access."""
        if isinstance(index, slice):
            slice_objs = self.__class__()
            slice_objs.objects = self.objects[index]
            return slice_objs
        return self.objects[index]

    def __len__(self):
        """List length."""
        return len(self.objects)

    def __iter__(self):
        """Iterator to iterate over objects list."""
        return iter(self.objects)

    @classmethod
    def obj_class(cls):
        obj_type = get_type_hints(cls).get('objects').__args__
        return obj_type and obj_type[0]

    @classmethod
    def _make_list(cls, inst_list, db_inst_list, expected_attrs=None):
        obj_cls = cls.obj_class()
        for db_inst in db_inst_list:
            inst = obj_cls._from_db_object(obj_cls(), db_inst, expected_attrs)
            inst_list.objects.append(inst)

        return inst_list

    @classmethod
    def from_primitive(cls, primitive):
        obj_cls = cls.obj_class()
        return cls(objects=[obj_cls(**primitive) for primitive in primitive])

    def to_primitive(self):
        primitive = list()
        for obj in self.objects:
            if isinstance(obj, BaseObject):
                obj = obj.to_primitive()
            primitive.append(obj)
        return primitive
