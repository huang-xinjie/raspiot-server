from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class Room(db.Model):
    __tablename__ = 'rooms'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    devices = db.relationship('Device', backref='room')
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)
    deleted_at = db.Column(db.DateTime)

    def __repr__(self):
        return '<Room %r>' % self.name


class Device(db.Model):
    __tablename__ = 'devices'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uuid = db.Column(db.String(36), nullable=False)
    name = db.Column(db.String(64), unique=True)
    created_at = db.Column(db.DateTime)
    ip = db.Column(db.String(16))
    mac = db.Column(db.String(12))
    status = db.Column(db.String(20), unique=True)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'))
    updated_at = db.Column(db.DateTime)
    launched_at = db.Column(db.DateTime)
    deleted_at = db.Column(db.DateTime)

    def __repr__(self):
        return '<Device %r>' % self.name


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, unique=True, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    passwordHash = db.Column(db.String(128))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)
    deleted_at = db.Column(db.DateTime)

    def __repr__(self):
        return '<User %r>' % self.username

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.passwordHash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.passwordHash, password)

    def generate_confirmation_token(self, expiration=7200):
        pass


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    rolename = db.Column(db.String(20), unique=True)
    users = db.relationship(User, backref='role')

    def __repr__(self):
        return '<Role %r>' % self.rolename
