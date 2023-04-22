from datetime import datetime
from db.sqlalchemy import models
from sqlalchemy.orm import subqueryload


def create_role(values):
    db_role = models.Role()
    db_role.update({'name': values.get('name')})
    models.db.session.add(db_role)
    models.db.session.commit()

    models.db.session.refresh(db_role)
    return db_role


def get_role_by_name(role_name):
    role = models.Role.query.filter_by(name=role_name).options(subqueryload('users')).first()
    return role


def get_role_by_id(role_id):
    role = models.Role.query.filter_by(id=role_id).options(subqueryload('users')).first()
    return role


def get_all_role():
    role_list = models.Role.query.options(subqueryload('users')).all()
    return role_list


def _get_updated_values(model_cls, values):
    updated_values = {}
    for k, v in values.items():
        if k in model_cls.db_update_fields():
            updated_values[k] = v

    return updated_values


def update_role(role_id, values):
    updated_values = _get_updated_values(models.Role, values)

    models.Role.query.filter(models.Role.id == role_id).update(updated_values)
    models.db.session.commit()


def delete_role(role_id):
    models.Role.query.filter(models.Role.id == role_id).delete()
    models.db.session.commit()


def create_user(values):
    db_user = models.User()
    db_user.update({'name': values.get('name'),
                    'uuid': values.get('uuid'),
                    'email': values.get('email'),
                    'password_hash': values.get('password_hash'),
                    'role_id': values.get('role_id')})
    models.db.session.add(db_user)
    models.db.session.commit()

    models.db.session.refresh(db_user)
    return db_user


def get_user_by_name(user_name):
    user = models.User.query.filter_by(name=user_name).options(subqueryload('rooms')).first()
    return user


def get_user_by_uuid(uuid):
    user = models.db.session.query(models.User).filter_by(uuid=uuid).first()
    return user


def get_all_user():
    user_list = models.User.query.options(subqueryload('rooms')).all()
    return user_list


def update_user(user_id, values):
    updated_values = _get_updated_values(models.User, values)

    models.User.query.filter(models.User.id == user_id).update(updated_values)
    models.db.session.commit()


def delete_user(user_id):
    models.User.query.filter(models.User.id == user_id).delete()
    models.db.session.commit()


def create_room(values):
    db_room = models.Room()
    db_room.update({'name': values.get('name')})
    models.db.session.add(db_room)
    models.db.session.commit()

    models.db.session.refresh(db_room)
    return db_room


def get_room_by_name(room_name):
    room = models.Room.query.filter_by(name=room_name).options(subqueryload('devices')).first()
    return room


def get_all_room():
    room_list = models.Room.query.options(subqueryload('devices')).all()
    return room_list


def update_room(room_id, values):
    updated_values = _get_updated_values(models.Room, values)

    models.Room.query.filter(models.Room.id == room_id).update(updated_values)
    models.db.session.commit()


def delete_room(room_id):
    models.Room.query.filter(models.Room.id == room_id).delete()
    models.db.session.commit()


def create_device(values):
    db_device = models.Device()
    db_device.update(
        {'uuid': values.get('uuid'),
         'name': values.get('name'),
         'mac_addr': values.get('mac_addr'),
         'ipv4_addr': values.get('ipv4_addr'),
         'ipv6_addr': values.get('ipv6_addr'),
         'status': values.get('status')})
    models.db.session.add(db_device)
    models.db.session.commit()

    models.db.session.refresh(db_device)
    return db_device


def get_device_by_uuid(uuid):
    filters = {'uuid': uuid}
    devices = get_devices_by_filters(filters)
    return devices[0] if devices else None


def get_device_by_mac_addr(mac_addr):
    filters = {'mac_addr': mac_addr}
    devices = get_devices_by_filters(filters)
    return devices[0] if devices else None


def create_device_detail(values):
    db_detail = models.DeviceDetail()
    db_detail.update({'name': values['name'],
                      'type': values['type'],
                      'value': values['value'],
                      'read_only': values.get('read_only'),
                      'value_range': values.get('value_range'),
                      'device_id': values['device_id']})
    models.db.session.add(db_detail)
    models.db.session.commit()

    return db_detail


def _update_details_to_db(device_id, details):
    if not details:
        return

    details_mapping = {d['name']: d for d in details}
    device_details = models.db.session.query(models.DeviceDetail).filter_by(device_id=device_id)
    exist_details = device_details.filter(models.DeviceDetail.name.in_(details_mapping.keys())).all()
    # remove details
    # device_details.filter(models.DeviceDetail.name.not_in(details_mapping.keys())).delete()

    for db_detail in exist_details:
        detail = details_mapping.pop(db_detail.name)
        if db_detail.value != detail['value']:
            db_detail.update({'value': detail['value']})

    for _, detail in details_mapping.items():
        detail['device_id'] = device_id
        create_device_detail(detail)
    models.db.session.commit()


def update_device(uuid, values):
    details = values.pop('details', None)
    device = models.db.session.query(models.Device).filter_by(uuid=uuid).first()
    if details:
        _update_details_to_db(device.id, details)

    updated_values = _get_updated_values(models.Device, values)
    device.update(updated_values)

    models.db.session.commit()


def get_devices_by_filters(filters, sort_key='created_at', sort_dir='desc', limit=None, marker=None):
    query_prefix = models.db.session.query(models.Device)
    if 'name' in filters:
        query_prefix = query_prefix.filter_by(name=filters.get('name'))

    if 'uuid' in filters:
        query_prefix = query_prefix.filter_by(uuid=filters.get('uuid'))

    if 'mac_addr' in filters:
        query_prefix = query_prefix.filter_by(mac_addr=filters.get('mac_addr'))

    devices = query_prefix.order_by(sort_key).all()
    return devices


def get_all_device():
    device_list = models.Device.query.all()
    return device_list


def delete_device(device_id):
    models.Device.query.filter(models.Device.id == device_id).delete()
    models.db.session.commit()
