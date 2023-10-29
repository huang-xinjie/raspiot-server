from enum import Enum, unique
from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class BaseModel(object):
    id = db.Column(db.Integer, unique=True, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
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
    is_public = db.Column(db.Boolean, default=True)
    updated_at = db.Column(db.DateTime, onupdate=datetime.now)

    devices = db.relationship('Device', backref='room')
    user_id = db.Column(db.String(36), db.ForeignKey('users.uuid'))

    @staticmethod
    def db_update_fields():
        return ['name', 'user_id', 'is_public']

    def __repr__(self):
        return f'<Room {self.name}>'


class MacMapping(db.Model, BaseModel):
    __tablename__ = 'mac_mappings'

    mac_addr = db.Column(db.String(18))
    ipv4_addr = db.Column(db.String(16))
    ipv6_addr = db.Column(db.String(40))

    @staticmethod
    def db_update_fields():
        return ['mac_addr', 'ipv4_addr', 'ipv6_addr']

    def __repr__(self):
        return f'<MacMapping {self.mac_addr}>'


@unique
class DeviceStatus(str, Enum):
    online = 'online'
    offline = 'offline'


@unique
class DeviceSyncMode(str, Enum):
    poll = 'poll'
    report = 'report'


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
    sync_mode = db.Column(db.Enum(DeviceSyncMode), default=DeviceSyncMode.poll)
    sync_interval = db.Column(db.Integer, default=60 * 5)

    status = db.Column(db.Enum(DeviceStatus), default=DeviceStatus.offline)
    synced_at = db.Column(db.DateTime)

    attrs = db.relationship('DeviceAttr', backref='device')
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'))

    @staticmethod
    def db_update_fields():
        return ['name', 'status', 'sync_mode', 'synced_at', 'sync_interval',
                'mac_addr', 'ipv4_addr', 'ipv6_addr', 'protocol', 'port', 'attrs', 'room_id']

    def __repr__(self):
        return f'<Device {self.name}>'


@unique
class DeviceAttrType(str, Enum):
    url = 'url'
    file = 'file'
    text = 'text'
    image = 'image'
    range = 'range'
    button = 'button'
    switch = 'switch'
    select = 'select'
    stream = 'stream'
    datetime = 'datetime'


class DeviceAttr(db.Model, BaseModel):
    __tablename__ = 'device_details'

    name = db.Column(db.String(64), nullable=False)
    type = db.Column(db.Enum(DeviceAttrType), nullable=False)
    value = db.Column(db.String(255), nullable=False)
    value_constraint = db.Column(db.String(255))
    read_only = db.Column(db.Boolean, default=False)

    device_id = db.Column(db.Integer, db.ForeignKey('devices.id'))

    @staticmethod
    def db_update_fields():
        return ['type', 'value', 'read_only', 'value_constraint']

    def __repr__(self):
        return f'<DeviceAttr {self.name}>'


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
        return ['name', 'email', 'role_id', 'password_hash']

    @property
    def is_admin(self):
        return bool(self.role and self.role.is_admin)

    def __repr__(self):
        return f'<User {self.name}>'


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
        return f'<Role {self.name}>'
