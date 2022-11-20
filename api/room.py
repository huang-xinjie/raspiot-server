import objects
from api import raspiot_api
from kernel.room_handler import RoomHandler

objects.register_all()


@raspiot_api.route('/rooms')
def get_rooms():
    objects.room.RoomList.get_all()
    room_handler = RoomHandler()
    room_list = room_handler.get_room_list()
    return {'rooms': room_list}


@raspiot_api.route('/room/<room_name>')
def get_room_detail(room_name):
    return {'room': room_name}


@raspiot_api.route('/room/<room_name>', methods=['POST'])
def add_room(room_name):
    room_handler = RoomHandler()
    room_list = room_handler.get_room_list()
    room_list.append(room_name)
    return {'rooms': room_list}
