from flask import Blueprint

raspiot_api = Blueprint('raspiot_api', __name__)


@raspiot_api.route('/')
def index(name=None):
    name = name or 'World'
    return 'Hello %s!' % name
