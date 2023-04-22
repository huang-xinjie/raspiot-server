from flask import jsonify
from flask import request
from werkzeug import exceptions

from log import log
from api import raspiot_api
from objects.role import Role
from objects.user import User, UserList


@raspiot_api.post('/user')
def add_user():
    email = request.form.get('email')
    user_name = request.form.get('name')
    password = request.form.get('password')
    role_name = request.form.get('role')
    if not (email and user_name and password and role_name):
        raise exceptions.BadRequest(description='parameter "%s" is invalid.' % email)
    user = User(uuid=User.generate_uuid(), name=user_name, email=email, password=password, role=role_name)
    try:
        user.create()
    except ValueError as e:
        raise exceptions.BadRequest(description='user %s already exists.' % user_name)
    except Exception as e:
        log.exception('create user failed: %s', e)
        raise exceptions.InternalServerError(description=str(e))
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


@raspiot_api.put('/user/<uuid>')
def update_user(uuid):
    user = User.get_by_uuid(uuid)
    if not user:
        raise exceptions.NotFound(description='user %s not found.' % uuid)

    role_name = request.form.get('role')
    role = Role.get_by_name(role_name)
    if not role:
        raise exceptions.NotFound(description='role %s not found.' % role_name)
    user.update(role_id=role.id)
    user.save()

    return _view(user)


@raspiot_api.delete('/user/<uuid>')
def delete_user(uuid):
    user = User.get_by_uuid(uuid)
    if not user:
        raise exceptions.NotFound(description='user %s not found.' % uuid)
    user.destroy()
    return {}, 204


def _view(user_obj):
    user_dict = dict(uuid=user_obj.get('uuid'),
                     name=user_obj.get('name'),
                     email=user_obj.get('email'),
                     role=user_obj.get('role'),
                     rooms=user_obj.get('rooms', []),
                     created_at=str(user_obj.get('created_at')))
    return user_dict


def _list_view(user_obj_list):
    user_list = []
    for user_obj in user_obj_list:
        user_list.append(_view(user_obj))

    return jsonify(user_list)
