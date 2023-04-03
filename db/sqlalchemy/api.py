from db.sqlalchemy import models
from sqlalchemy.orm import subqueryload


def create_user(values):
    db_user = models.User()
    db_user.update({'name': values.get('name'),
                    'uuid': values.get('uuid'),
                    'email': values.get('email'),
                    'created_at': values.get('created_at'),
                    'updated_at': values.get('updated_at')})
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
    updated_values = {}
    for k, v in values.items():
        if k in models.User.db_update_fields:
            updated_values[k] = v

    models.User.query.filter(models.User.id == user_id).update(updated_values)
    models.db.session.commit()


def create_room(values):
    db_room = models.Room()
    db_room.update({'name': values.get('name'),
                    'created_at': values.get('created_at'),
                    'updated_at': values.get('updated_at')})
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
    updated_values = {}
    for k, v in values.items():
        if k in models.Room.db_update_fields:
            updated_values[k] = v

    models.Room.query.filter(models.Room.id == room_id).update(updated_values)
    models.db.session.commit()


def create_device(values):
    db_device = models.Device()
    db_device.update(
        {'uuid': values.get('uuid'),
         'name': values.get('name'),
         'mac_addr': values.get('mac_addr'),
         'ipv4_addr': values.get('ipv4_addr'),
         'ipv6_addr': values.get('ipv6_addr'),
         'status': values.get('status'),
         'created_at': values.get('created_at')})
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


def update_device(uuid, values):
    updated_values = {}
    for k, v in values.items():
        if k in models.Device.db_update_fields():
            updated_values[k] = v

    models.Device.query.filter(models.Device.uuid == uuid).update(updated_values)
    models.db.session.commit()


def get_devices_by_filters(filters, sort_key='created_at', sort_dir='desc', limit=None, marker=None):
    query_prefix = models.db.session.query(models.Device)
    if 'name' in filters:
        query_prefix = query_prefix.filter_by(name=filters.get('name'))

    if 'uuid' in filters:
        query_prefix = query_prefix.filter_by(uuid=filters.get('uuid'))

    if 'mac_addr' in filters:
        query_prefix = query_prefix.filter_by(mac_addr=filters.get('mac_addr'))

    devices = query_prefix.all()
    return devices


def get_all_device():
    device_list = models.Device.query.all()
    return device_list
