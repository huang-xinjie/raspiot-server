from flask import jsonify
from flask import request
from werkzeug import exceptions

from log import log
from api import raspiot
from api import raspiot_api
from common import utils
from objects.room import Room, RoomList
from objects.device import Device, DeviceList


@raspiot_api.get('/rooms')
def get_rooms():
    room_list = RoomList.get_all()
    return _list_view(room_list)


@raspiot_api.get('/room/<room_name>')
def get_room_detail(room_name):
    room = Room.get_by_name(room_name)
    if not room:
        raise exceptions.NotFound(description='room %s not found.' % room_name)
    return _view(room)


@raspiot_api.post('/room')
def add_room():
    room_name = request.form.get('name')
    if not room_name:
        raise exceptions.BadRequest(description='room_name "%s" is invalid.' % room_name)

    room = Room(name=room_name, updated_at=utils.time_now())
    try:
        room.create()
    except ValueError:
        raise exceptions.BadRequest(description='room %s already exists.' % room_name)
    return _view(room)


@raspiot_api.post('/room/<room_name>/add_device')
def add_device_to_room(room_name):
    room = Room.get_by_name(room_name)
    if not room:
        raise exceptions.NotFound(description='room %s not found.' % room_name)

    device_uuid = request.form.get('device_uuid')
    device = Device.get_by_uuid(device_uuid)
    if not device:
        raise exceptions.BadRequest(description='device %s not found.' % device_uuid)
    elif device.name in room.devices:
        raise exceptions.BadRequest(description='device %s already in room %s.' % (device_uuid, room_name))

    device.move_to(room.id)
    room.refresh()

    return _view(room)


def _view(room_obj):
    room_dict = dict(name=room_obj.get('name'),
                     user_id=room_obj.get('user_id'),
                     is_public=room_obj.get('is_public'),
                     devices=room_obj.get('devices'),
                     updated_at=str(room_obj.get('updated_at')))
    return room_dict


def _list_view(room_obj_list):
    room_list = []
    for room_obj in room_obj_list:
        room_list.append(_view(room_obj))

    return jsonify(room_list)
