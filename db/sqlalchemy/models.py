from enum import Enum, unique
from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

from common.constants import STANDARD_INITIAL_TIME

db = SQLAlchemy()


class BaseModel(object):
    id = db.Column(db.Integer, unique=True, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, onupdate=datetime.now)
    deleted_at = db.Column(db.DateTime)

    @staticmethod
    def db_update_fields():
        return ['updated_at', 'deleted_at']

    def update(self, values):
        for k, v in values.items():
            setattr(self, k, v)

    def get(self, key, default=None):
        return getattr(self, key, default)


class Room(db.Model, BaseModel):
    __tablename__ = 'rooms'

    name = db.Column(db.String(64), unique=True)
    updated_at = db.Column(db.DateTime, default=STANDARD_INITIAL_TIME)
    is_public = db.Column(db.Boolean, default=True)

    devices = db.relationship('Device', backref='room')
    user_id = db.Column(db.String(36), db.ForeignKey('users.uuid'))

    @staticmethod
    def db_update_fields():
        return ['name', 'user_id', 'is_public', 'updated_at', 'deleted_at']

    def __repr__(self):
        return '<Room %r>' % self.name


@unique
class DeviceStatus(str, Enum):
    online = 'online'
    offline = 'offline'


@unique
class DeviceProtocol(str, Enum):
    ble = 'ble'
    tcp = 'tcp'
    udp = 'udp'
    http = 'http'


class Device(db.Model, BaseModel):
    __tablename__ = 'devices'

    uuid = db.Column(db.String(36), nullable=False, unique=True)
    name = db.Column(db.String(64), nullable=False)
    mac_addr = db.Column(db.String(18))
    ipv4_addr = db.Column(db.String(16))
    ipv6_addr = db.Column(db.String(40))
    protocol = db.Column(db.Enum(DeviceProtocol))
    port = db.Column(db.Integer)
    status = db.Column(db.Enum(DeviceStatus))
    launched_at = db.Column(db.DateTime)

    details = db.relationship('DeviceDetail', backref='device')
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'))

    @staticmethod
    def db_update_fields():
        return ['name', 'status', 'updated_at', 'deleted_at', 'launched_at',
                'ipv4_addr', 'ipv6_addr', 'protocol', 'port', 'details', 'room_id']

    def __repr__(self):
        return '<Device %r>' % self.name


@unique
class DeviceDetailType(Enum):
    text = 'text'
    switch = 'switch'
    image = 'image'
    button = 'button'


class DeviceDetail(db.Model, BaseModel):
    __tablename__ = 'device_details'

    name = db.Column(db.String(64), nullable=False)
    type = db.Column(db.Enum(DeviceDetailType), nullable=False)
    value = db.Column(db.String(255), nullable=False)
    read_only = db.Column(db.Boolean, default=False)
    value_range = db.Column(db.String(255))

    device_id = db.Column(db.Integer, db.ForeignKey('devices.id'))

    @staticmethod
    def db_update_fields():
        return ['name', 'updated_at']

    def __repr__(self):
        return '<DeviceDetail %r>' % self.name


class User(db.Model, BaseModel):
    __tablename__ = 'users'

    uuid = db.Column(db.String(36), nullable=False, unique=True, index=True)
    email = db.Column(db.String(64), unique=True, index=True)
    name = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))

    rooms = db.relationship('Room', backref='user')
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    @staticmethod
    def db_update_fields():
        return ['name', 'email', 'role_id', 'password_hash', 'updated_at', 'deleted_at']

    @property
    def is_admin(self):
        return bool(self.role and self.role.is_admin)

    def __repr__(self):
        return '<User %r>' % self.username


class RoleEnum(str, Enum):
    admin = 'admin'
    member = 'member'
    guest = 'guest'


class Role(db.Model, BaseModel):
    __tablename__ = 'roles'

    name = db.Column(db.Enum(RoleEnum.admin, RoleEnum.member, RoleEnum.guest), unique=True)
    users = db.relationship(User, backref='role')

    @property
    def is_admin(self):
        return self.name == RoleEnum.admin

    def __repr__(self):
        return '<Role %r>' % self.name
