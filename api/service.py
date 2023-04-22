from flask import Flask

from api import raspiot_api
from config.api import app_config
from db.sqlalchemy.models import db, RoleEnum
from objects.role import Role, RoleList


def init_db(app, app_db):
    app_db.init_app(app)
    with app.app_context():
        app_db.create_all()

        roles = RoleList.get_all()
        created_roles = [role.name for role in roles]
        for role in RoleEnum:
            if role not in created_roles:
                Role(name=role).create()


def create(config_name):
    app = Flask(__name__)
    app.config.from_object(app_config[config_name])

    init_db(app, db)
    app.register_blueprint(raspiot_api)

    return app
