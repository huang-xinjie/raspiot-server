from flask import Flask
from fastapi import FastAPI

from api import raspiot
from api import raspiot_api
from config.api import app_config
from db.sqlalchemy.models import db


def create(config_name):
    api = FastAPI()
    api.include_router(raspiot)

    app = Flask(__name__)
    app.config.from_object(app_config[config_name])

    db.init_app(app)

    app.register_blueprint(raspiot_api)
    with app.app_context():
        db.create_all()

    return api, app
