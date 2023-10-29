import uuid
from flask import Blueprint, request, g

raspiot_api = Blueprint('raspiot_api', __name__)
from api import auth, users, rooms, devices, images, exceptions


@raspiot_api.before_request
def set_request_id():
    g.request_id = request.headers.get('X-Request-ID', str(uuid.uuid4()))


@raspiot_api.get('/<name>')
def index(name='World'):
    return f'Hello {name}!'
