from flask import jsonify


def root_view(room_obj):
    room_dict = dict(name=room_obj.get('name'),
                     user_id=room_obj.get('user_id'),
                     is_public=room_obj.get('is_public'),
                     devices=room_obj.get('devices'),
                     updated_at=str(room_obj.get('updated_at')))
    return room_dict


def room_list_view(room_obj_list):
    room_list = []
    for room_obj in room_obj_list:
        room_list.append(root_view(room_obj))

    return jsonify(room_list)
