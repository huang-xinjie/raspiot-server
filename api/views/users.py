from flask import jsonify


def user_view(user_obj):
    user_dict = dict(uuid=user_obj.get('uuid'),
                     name=user_obj.get('name'),
                     email=user_obj.get('email'),
                     role=user_obj.get('role'),
                     rooms=user_obj.get('rooms', []),
                     created_at=str(user_obj.get('created_at')))
    return user_dict


def user_list_view(user_obj_list):
    user_list = []
    for user_obj in user_obj_list:
        user_list.append(user_view(user_obj))

    return jsonify(user_list)
