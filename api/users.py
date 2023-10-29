from flask import request
from werkzeug import exceptions

import log
from api import raspiot_api
from api.views.users import user_view, user_list_view
from objects.role import Role
from objects.user import User, UserList


@raspiot_api.post('/user')
def add_user():
    email = request.form.get('email')
    user_name = request.form.get('name')
    password = request.form.get('password')
    role_name = request.form.get('role')
    if not (email and user_name and password and role_name):
        raise exceptions.BadRequest(description=f'parameter {email} is invalid')
    user = User(uuid=User.generate_uuid(), name=user_name, email=email, password=password, role=role_name)
    try:
        user.create()
    except ValueError as e:
        raise exceptions.BadRequest(description=f'user {user_name} already exists')
    except Exception as e:
        log.exception(f'create user failed: {e}')
        raise exceptions.InternalServerError(description=str(e))
    return user_view(user)


@raspiot_api.get('/user/<uuid>')
def get_user_detail(uuid):
    user = User.get_by_uuid(uuid)
    if not user:
        raise exceptions.NotFound(description=f'user {uuid} not found')
    return user_view(user)


@raspiot_api.get('/users')
def get_users():
    user_list = UserList.get_all()
    return user_list_view(user_list)


@raspiot_api.put('/user/<uuid>')
def update_user(uuid):
    user = User.get_by_uuid(uuid)
    if not user:
        raise exceptions.NotFound(description=f'user {uuid} not found')

    role_name = request.form.get('role')
    role = Role.get_by_name(role_name)
    if not role:
        raise exceptions.NotFound(description=f'role {role_name} not found')
    user.update(role_id=role.id)
    user.save()

    return user_view(user)


@raspiot_api.delete('/user/<uuid>')
def delete_user(uuid):
    user = User.get_by_uuid(uuid)
    if not user:
        raise exceptions.NotFound(description=f'user {uuid} not found')
    user.destroy()
    return {}, 204
