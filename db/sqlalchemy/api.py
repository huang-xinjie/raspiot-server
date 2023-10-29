import json

from sqlalchemy.orm import subqueryload

from common import exceptions
from db.sqlalchemy import models


def _get_updated_values(model_cls, values):
    updated_values = {}
    for k, v in values.items():
        if k in model_cls.db_update_fields():
            updated_values[k] = v

    return updated_values


def _update_db_by_id(model_cls, db_id, values):
    updated_values = _get_updated_values(model_cls, values)

    model_cls.query.filter(model_cls.id == db_id).update(updated_values)
    models.db.session.commit()


def _destroy_by_id(model_cls, db_id):
    model_cls.query.filter(model_cls.id == db_id).delete()
    models.db.session.commit()


def create_role(values):
    db_role = models.Role()
    db_role.update({'name': values.get('name')})
    models.db.session.add(db_role)
    models.db.session.commit()

    models.db.session.refresh(db_role)
    return db_role


def get_role_by_name(role_name):
    role = models.Role.query.filter_by(name=role_name).options(subqueryload(models.Role.users)).first()
    return role


def get_role_by_id(role_id):
    role = models.Role.query.filter_by(id=role_id).options(subqueryload(models.Role.users)).first()
    return role


def get_all_role():
    role_list = models.Role.query.options(subqueryload(models.Role.users)).all()
    return role_list


def update_role(role_id, values):
    updated_values = _get_updated_values(models.Role, values)

    models.Role.query.filter(models.Role.id == role_id).update(updated_values)
    models.db.session.commit()


def delete_role(role_id):
    models.Role.query.filter(models.Role.id == role_id).delete()
    models.db.session.commit()


def create_user(values):
    db_user = models.User()
    db_user.update(_get_updated_values(models.User, values))
    db_user.update({'uuid': values.get('uuid')})
    models.db.session.add(db_user)
    models.db.session.commit()

    models.db.session.refresh(db_user)
    return db_user


def get_user_by_name(user_name):
    query_prefix = models.User.query.filter_by(name=user_name).options(subqueryload(models.User.rooms))
    user = query_prefix.options(subqueryload(models.User.role_id)).first()
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
    room = models.Room.query.filter_by(name=room_name).options(subqueryload(models.Room.devices)).first()
    return room


def get_all_room():
    room_list = models.Room.query.options(subqueryload(models.Room.devices)).all()
    return room_list


def update_room(room_id, values):
    updated_values = _get_updated_values(models.Room, values)

    models.Room.query.filter(models.Room.id == room_id).update(updated_values)
    models.db.session.commit()


def delete_room(room_id):
    models.Room.query.filter(models.Room.id == room_id).delete()
    models.db.session.commit()


def create_mac_mapping(values):
    db_mac_mapping = models.MacMapping()
    db_mac_mapping.update(_get_updated_values(models.MacMapping, values))
    models.db.session.add(db_mac_mapping)
    models.db.session.commit()

    models.db.session.refresh(db_mac_mapping)
    return db_mac_mapping


def get_mapping_by_mac_addr(mac_addr):
    room = models.MacMapping.query.filter_by(mac_addr=mac_addr).first()
    return room


def get_all_mac_mapping():
    room_list = models.MacMapping.query.all()
    return room_list


def update_mac_mapping(mapping_id, values):
    updated_values = _get_updated_values(models.MacMapping, values)

    models.MacMapping.query.filter(models.MacMapping.id == mapping_id).update(updated_values)
    models.db.session.commit()


def delete_mac_mapping(mapping_id):
    models.MacMapping.query.filter(models.MacMapping.id == mapping_id).delete()
    models.db.session.commit()


def create_device(values):
    db_device = models.Device()
    db_device.update({'uuid': values.get('uuid')})
    db_device.update(_get_updated_values(models.Device, values))
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


def create_device_attr(device_id, values):
    db_attr = models.DeviceAttr()
    db_attr.update({'device_id': device_id})
    db_attr.update({'name': values['name']})
    db_attr.update(_get_updated_values(models.DeviceAttr, values))
    db_attr.update({'value_constraint': json.dumps(values.get('value_constraint'))})
    models.db.session.add(db_attr)
    models.db.session.commit()

    return db_attr


def _update_attrs_to_db(device_id, attrs):
    if not attrs:
        return

    attrs_mapping = {d['name']: d for d in attrs}
    device_attrs = models.db.session.query(models.DeviceAttr).filter_by(device_id=device_id)
    exist_attrs = device_attrs.filter(models.DeviceAttr.name.in_(attrs_mapping.keys())).all()
    # remove attrs
    device_attrs.filter(models.DeviceAttr.name.not_in(attrs_mapping.keys())).delete()
    # update attrs
    for db_attr in exist_attrs:
        attr = attrs_mapping.pop(db_attr.name)
        attr['value_constraint'] = json.dumps(attr.get('value_constraint'))
        for field in models.DeviceAttr.db_update_fields():
            if getattr(db_attr, field) != attr.get(field):
                db_attr.update({field: attr.get(field)})
    # add attrs
    for _, attr in attrs_mapping.items():
        create_device_attr(device_id, attr)
    models.db.session.commit()


def update_device(uuid, values):
    device = models.db.session.query(models.Device).filter_by(uuid=uuid).first()
    if not device:
        raise exceptions.DeviceNotFound(device_uuid=uuid)

    attrs = values.pop('attrs', None)
    if attrs:
        _update_attrs_to_db(device.id, attrs)

    updated_values = _get_updated_values(models.Device, values)
    device.update(updated_values)

    models.db.session.commit()


def get_devices_by_filters(filters, sort_key='created_at', sort_dir='desc', limit=None, marker=None):
    query_prefix = models.db.session.query(models.Device)
    if 'name' in filters:
        query_prefix = query_prefix.filter_by(name=filters.pop('name'))

    if 'uuid' in filters:
        query_prefix = query_prefix.filter_by(uuid=filters.pop('uuid'))

    if 'mac_addr' in filters:
        query_prefix = query_prefix.filter_by(mac_addr=filters.pop('mac_addr'))

    if 'room' in filters:
        room = get_room_by_name(filters.pop('room'))
        room_id = room.id if room else -1
        query_prefix = query_prefix.filter_by(room_id=room_id)

    devices = query_prefix.options(subqueryload(models.Device.attrs)).order_by(sort_key).all()
    return devices


def get_all_device():
    device_list = models.Device.query.all()
    return device_list


def delete_device(device_id):
    models.DeviceAttr.query.filter(models.DeviceAttr.device_id == device_id).delete()
    models.Device.query.filter(models.Device.id == device_id).delete()
    models.db.session.commit()
