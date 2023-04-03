from flask import jsonify
from flask import request
from werkzeug import exceptions
from pydantic import root_validator

from log import log
from api import raspiot_api
from objects.device import Device, DeviceList


class DeviceRequest(Device):
    @root_validator(pre=True)
    def validate_fields(cls, values):
        if all(x is None for x in [values.get('mac_addr'), values.get('ipv4_addr'), values.get('ipv6_addr')]):
            raise ValueError('At least one of the fields "mac_addr", "ipv4_addr", "ipv6_addr" is required')

        return values


@raspiot_api.post('/device')
def add_device():
    device_name = request.form.get('name')
    mac_addr = request.form.get('mac_addr')
    if not (mac_addr and Device.validate_mac_addr(mac_addr)):
        raise exceptions.BadRequest(description='mac_addr "%s" is invalid.' % mac_addr)
    device = Device(uuid=Device.generate_uuid(mac_addr), name=device_name, mac_addr=mac_addr)
    try:
        device.create()
    except ValueError:
        raise exceptions.BadRequest(description='device with mac addr (%s) already exists.' % mac_addr)
    return _view(device)


@raspiot_api.get('/device/<uuid>')
def get_device_detail(uuid):
    device = Device.get_by_uuid(uuid)
    if not device:
        raise exceptions.NotFound(description='device %s not found.' % uuid)
    return _view(device)


@raspiot_api.get('/devices')
def get_devices_of_room():
    device_list = DeviceList.get_all()
    return _list_view(device_list)


@raspiot_api.put('/device/<uuid>')
def update_device(uuid):
    device = Device.get_by_uuid(uuid)
    if not device:
        raise exceptions.NotFound(description='device %s not found.' % uuid)

    device_name = request.form.get('name')
    device.update(name=device_name)
    device.save()

    return _view(device)


def _view(device_obj):
    device_dict = dict(uuid=device_obj.get('uuid'),
                       name=device_obj.get('name'),
                       mac_addr=device_obj.get('mac_addr'),
                       ipv4_addr=device_obj.get('ipv4_addr'),
                       ipv6_addr=device_obj.get('ipv6_addr'),
                       created_at=str(device_obj.get('created_at')))
    return device_dict


def _list_view(device_obj_list):
    device_list = []
    for device_obj in device_obj_list:
        device_list.append(_view(device_obj))

    return jsonify(device_list)
