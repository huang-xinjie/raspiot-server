from flask import Blueprint
from fastapi import APIRouter

raspiot_api = Blueprint('raspiot_api', __name__)
raspiot = APIRouter()


from api import auth, user, room, device, exception


@raspiot_api.get('/')
def index(name=None):
    name = name or 'World'
    return 'Hello %s!' % name


@raspiot.get('/')
def index(name: str = 'World'):
    return 'Hello %s!' % name
