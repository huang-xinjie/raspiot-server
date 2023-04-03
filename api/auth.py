from flask import jsonify
from werkzeug import exceptions

from api import raspiot_api
from objects.user import User


@raspiot_api.get('/auth/token')
def get_token():
    return {'token': 'fake_token'}
