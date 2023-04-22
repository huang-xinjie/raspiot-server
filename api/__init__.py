from flask import Blueprint

raspiot_api = Blueprint('raspiot_api', __name__)


from api import auth, user, room, device, exception


@raspiot_api.get('/')
def index(name='World'):
    return 'Hello %s!' % name

