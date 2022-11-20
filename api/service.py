from flask import Flask

from api import raspiot_api
from config.api import config
from api import room
from api import device


def create(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    app.register_blueprint(raspiot_api)

    return app
