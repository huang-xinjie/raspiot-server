from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

from common.constants import STANDARD_INITIAL_TIME

db = SQLAlchemy()


class BaseModel(object):
    id = db.Column(db.Integer, unique=True, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime)
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
        return ['name', 'is_public', 'updated_at', 'deleted_at']

    def __repr__(self):
        return '<Room %r>' % self.name


class Device(db.Model, BaseModel):
    __tablename__ = 'devices'

    uuid = db.Column(db.String(36), nullable=False, unique=True)
    name = db.Column(db.String(64))
    mac_addr = db.Column(db.String(18))
    ipv4_addr = db.Column(db.String(16))
    ipv6_addr = db.Column(db.String(40))
    status = db.Column(db.String(20))
    launched_at = db.Column(db.DateTime)

    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'))

    @staticmethod
    def db_update_fields():
        return ['name', 'status', 'updated_at', 'deleted_at', 'launched_at', 'room_id']

    def __repr__(self):
        return '<Device %r>' % self.name


class User(db.Model, BaseModel):
    __tablename__ = 'users'

    uuid = db.Column(db.String(36), nullable=False, unique=True, index=True)
    email = db.Column(db.String(64), unique=True, index=True)
    name = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=True)

    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    rooms = db.relationship('Room', backref='user')

    def __repr__(self):
        return '<User %r>' % self.username

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=7200):
        pass


class Role(db.Model, BaseModel):
    __tablename__ = 'roles'

    rolename = db.Column(db.String(20), unique=True)
    users = db.relationship(User, backref='role')

    def __repr__(self):
        return '<Role %r>' % self.rolename
