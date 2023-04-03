from flask import jsonify
from flask import request
from werkzeug import exceptions

from api import raspiot_api
from objects.user import User, UserList


@raspiot_api.post('/user')
def add_user():
    email = request.form.get('email')
    user_name = request.form.get('name')
    if not (email and user_name):
        raise exceptions.BadRequest(description='email "%s" is invalid.' % email)
    user = User(uuid=User.generate_uuid(user_name), name=user_name, email=email, is_admin=True)
    try:
        user.create()
    except ValueError:
        raise exceptions.BadRequest(description='user %s already exists.' % user_name)
    return _view(user)


@raspiot_api.get('/user/<uuid>')
def get_user_detail(uuid):
    user = User.get_by_uuid(uuid)
    if not user:
        raise exceptions.NotFound(description='user %s not found.' % uuid)
    return _view(user)


@raspiot_api.get('/users')
def get_users():
    user_list = UserList.get_all()
    return _list_view(user_list)


def _view(user_obj):
    user_dict = dict(uuid=user_obj.get('uuid'),
                     name=user_obj.get('name'),
                     email=user_obj.get('email'),
                     rooms=user_obj.get('rooms', []),
                     created_at=str(user_obj.get('created_at')))
    return user_dict


def _list_view(user_obj_list):
    user_list = []
    for user_obj in user_obj_list:
        user_list.append(_view(user_obj))

    return jsonify(user_list)
