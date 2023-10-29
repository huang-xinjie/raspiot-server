from flask import request
from werkzeug import exceptions

from api import raspiot_api
from api.views.rooms import root_view, room_list_view
from objects.device import Device
from objects.room import Room, RoomList


@raspiot_api.get('/rooms')
def get_rooms():
    room_list = RoomList.get_all()
    return room_list_view(room_list)


@raspiot_api.get('/room/<room_name>')
def get_room_detail(room_name):
    room = Room.get_by_name(room_name)
    if not room:
        raise exceptions.NotFound(description=f'room {room_name} not found')
    return root_view(room)


@raspiot_api.post('/room')
def add_room():
    room_name = request.form.get('name')
    if not room_name:
        raise exceptions.BadRequest(description=f'room_name {room_name} is invalid')

    room = Room(name=room_name)
    try:
        room.create()
    except ValueError:
        raise exceptions.BadRequest(description=f'room {room_name} already exists')
    return root_view(room)


@raspiot_api.post('/room/<room_name>/add_device')
def add_device_to_room(room_name):
    room = Room.get_by_name(room_name)
    if not room:
        raise exceptions.NotFound(description=f'room {room_name} not found')

    device_uuid = request.form.get('device_uuid')
    device = Device.get_by_uuid(device_uuid)
    if not device:
        raise exceptions.BadRequest(description=f'device {device_uuid} not found')
    elif device.name in room.devices:
        raise exceptions.BadRequest(description=f'device {device_uuid} already in room {room_name}')

    device.move_to(room)
    room.refresh()

    return root_view(room)

