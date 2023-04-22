from flask import jsonify
from flask import request
from werkzeug import exceptions
from pydantic import root_validator

from log import log
from api import raspiot_api
from common import exception as exc
from objects.device import Device, DeviceList
from iot.device.driver import HttpDeviceDriver


class DeviceAccessRequest(Device):
    @root_validator(pre=True)
    def validate_fields(cls, values):
        if not values.get('mac_addr'):
            raise ValueError('Field "mac_addr" is required')
        elif any(x for x in [values.get('ipv4_addr'), values.get('ipv6_addr')]) and not values.get('port'):
            raise ValueError('Field "port" is required with "ipv4_addr" or "ipv6_addr"')

        return values


@raspiot_api.post('/device')
def add_device():
    device_name = request.form.get('name')
    mac_addr = request.form.get('mac_addr')
    if not (mac_addr and Device.validate_mac_addr(mac_addr)):
        raise exceptions.BadRequest(description=f'mac_addr "{mac_addr}" is invalid.')
    device = Device(uuid=Device.generate_uuid(), name=device_name, mac_addr=mac_addr)
    try:
        device.create()
    except ValueError:
        raise exceptions.BadRequest(description=f'device with mac addr ({mac_addr}) already exists.')
    return _view(device)


@raspiot_api.get('/device/<uuid>')
def get_device_detail(uuid):
    device = Device.get_by_uuid(uuid)
    if not device:
        raise exceptions.NotFound(description=f'device {uuid} not found.')

    driver = HttpDeviceDriver()
    details = driver.get_device_details(device)
    device.update(details=details)
    device.save()
    return _view(device)


@raspiot_api.get('/devices')
def get_devices_of_room():
    device_list = DeviceList.get_all()
    return _list_view(device_list)


@raspiot_api.put('/device/<uuid>')
def update_device(uuid):
    device = Device.get_by_uuid(uuid)
    if not device:
        raise exceptions.NotFound(description=f'device {uuid} not found.')

    device_name = request.form.get('name')
    device.update(name=device_name)
    device.save()

    return _view(device)


@raspiot_api.put('/device/<uuid>/detail')
def set_device_detail_value(uuid):
    device = Device.get_by_uuid(uuid)
    if not device:
        raise exceptions.NotFound(description=f'device {uuid} not found.')

    detail_name = request.form.get('detail')
    value = request.form.get('value')
    driver = HttpDeviceDriver()
    try:
        details = driver.set_device_detail(device, detail_name, value)
    except exc.DeviceError as e:
        raise exceptions.BadHost(description=str(e))
    device.update(details=details)
    device.save()
    return _view(device)


@raspiot_api.post('/device/access')
def device_access():
    mac_addr = request.form.get('mac_addr')
    device = Device.get_by_mac_addr(mac_addr)
    if not device:
        raise exceptions.NotFound(description=f'device {mac_addr} not found.')

    ipv4_addr, ipv6_addr = request.form.get('ipv4_addr'), request.form.get('ipv6_addr')
    port = request.form.get('port')

    device.update(mac_addr=mac_addr, ipv4_addr=ipv4_addr, ipv6_addr=ipv6_addr, port=port)
    device.online()
    device.save()

    return _view(device)


@raspiot_api.post('/device/<uuid>/heartbeat')
def device_heartbeat(uuid):
    device = Device.get_by_uuid(uuid)
    if not device:
        raise exceptions.NotFound(description=f'device {uuid} not found.')

    device.online()
    return 'ACK'


def _view(device_obj):
    device_dict = dict(uuid=device_obj.get('uuid'),
                       name=device_obj.get('name'),
                       status=device_obj.get('status'),
                       mac_addr=device_obj.get('mac_addr'),
                       ipv4_addr=device_obj.get('ipv4_addr'),
                       ipv6_addr=device_obj.get('ipv6_addr'),
                       details=device_obj.get('details'),
                       created_at=str(device_obj.get('created_at')))
    return device_dict


def _list_view(device_obj_list):
    device_list = []
    for device_obj in device_obj_list:
        device_list.append(_view(device_obj))

    return jsonify(device_list)
