from flask import Flask

import objects
from api import raspiot_api
from config.api import app_config
from db.sqlalchemy.models import db, RoleEnum
from objects.role import Role, RoleList
from objects.room import Room


objects.register_all()


def init_database(app, app_db):
    app_db.init_app(app)
    with app.app_context():
        app_db.create_all()

        default_room = app.config.get('DEFAULT_ROOM')
        room = Room.get_by_name(default_room)
        if not room:
            Room(name=default_room).create()

        roles = RoleList.get_all()
        created_roles = [role.name for role in roles]
        for role in RoleEnum:
            if role not in created_roles:
                Role(name=role).create()


def create(config_mode='default', external_config=None, register_all=True):
    app = Flask('raspiot-server')
    app.config.from_object(app_config[config_mode])
    app.config.update(external_config or {})
    init_database(app, db)

    if not register_all:
        return app

    app.register_blueprint(raspiot_api)

    return app
