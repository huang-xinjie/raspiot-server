from flask import request, current_app
from pydantic import root_validator, ValidationError
from werkzeug import exceptions

import log
from api import raspiot_api
from api.views.devices import device_view, device_list_view
from common import exceptions as exc
from objects.device import Device, DeviceList
from objects.room import Room


class DeviceReportRequest(Device):
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
    ipv4_addr = request.form.get('ipv4_addr')
    protocol = request.form.get('protocol')
    port = request.form.get('port')
    room_name = request.form.get('room')

    try:
        mac_addr = Device.validate_mac_addr(mac_addr)
        device_manager_api = current_app.config.get('device_manager_api')
        ipv4_addr = ipv4_addr or device_manager_api.get_ip_by_mac_addr(mac_addr)
        room_name = room_name or current_app.config['DEFAULT_ROOM']
        room = Room.get_by_name(room_name)
        if not room:
            raise exceptions.NotFound(description=f'room {room_name} not found, must create a room before add device.')

        device = Device(uuid=Device.generate_uuid(), name=device_name,
                        mac_addr=mac_addr, ipv4_addr=ipv4_addr, protocol=protocol, port=port)
        device.create()
        device.move_to(room)
    except ValueError:
        raise exceptions.BadRequest(description=f'mac_addr "{mac_addr}" is invalid.')
    except AttributeError as e:
        log.error(f'add device failed: {e}')
        raise exceptions.BadRequest(description=f'device with mac addr ({mac_addr}) already exists.')
    return device_view(device)


@raspiot_api.get('/devices')
def get_devices():
    filters = {}
    supported_query_key = ['room', 'uuid', 'name', 'mac_addr']
    for k, v in request.args.items():
        if k in supported_query_key:
            filters[k] = v

    device_list = DeviceList.get_by_filters(filters=filters)
    return device_list_view(device_list, exclude_keys=['attrs'])


@raspiot_api.put('/device/<uuid>')
def update_device(uuid):
    expected_update_fields = {}
    device = Device.get_by_uuid(uuid)
    if not device:
        raise exceptions.NotFound(description=f'device {uuid} not found.')

    allowed_update_fields = ['name', 'mac_addr', 'ipv4_addr', 'ipv6_addr', 'protocol', 'port']
    for field, target in request.form.items():
        if field in allowed_update_fields:
            expected_update_fields[field] = target
        else:
            raise exceptions.BadRequest(description=f'Field {field} is not allowed to be updated.')

    try:
        device.update(expected_update_fields)
        device.save()
    except ValidationError as e:
        error_msg = ''.join([f'{error["loc"][0]}: {error["msg"]}' for error in e.errors()])
        raise exceptions.BadRequest(description=error_msg)

    return device_view(device)


@raspiot_api.get('/device/<uuid>')
def get_device_attrs(uuid):
    realtime = request.args.get('realtime')
    device = Device.get_by_uuid(uuid)
    if not device:
        raise exceptions.NotFound(description=f'device {uuid} not found.')

    try:
        realtime = str(realtime).lower() == 'true'
        if realtime or not device.attrs:
            device_manager_api = current_app.config.get('device_manager_api')
            attrs = device_manager_api.get_device_attrs(device)
            device.update(attrs=attrs)
            device.online()
            device.save()
    except exc.DeviceBasicAttributeError as e:
        device.offline()
        raise exceptions.BadHost(description=f'get device attrs realtime failed: {str(e)}')
    except exc.DeviceRemoteError:
        device.offline()

    return device_view(device)


@raspiot_api.put('/device/<uuid>/attr')
def set_device_attr(uuid):
    device = Device.get_by_uuid(uuid)
    if not device:
        raise exceptions.NotFound(description=f'device {uuid} not found.')

    attr_name = request.form.get('attr')
    value = request.form.get('value')

    for attr in device.attrs:
        if attr.name == attr_name:
            if attr.read_only:
                raise exceptions.BadRequest(description=f'attr [{attr_name}] of device {uuid} is read_only.')

    try:
        device_manager_api = current_app.config.get('device_manager_api')
        attrs = device_manager_api.set_device_attr(device, attr_name, value)
    except exc.DeviceRemoteError as e:
        raise exceptions.BadHost(description=str(e))
    device.update(attrs=attrs)
    device.save()
    return device_view(device)


@raspiot_api.delete('/device/<uuid>')
def remove_device(uuid):
    device = Device.get_by_uuid(uuid)
    if not device:
        raise exceptions.NotFound(description=f'device {uuid} not found.')

    device.destroy()
    return '', 204


@raspiot_api.post('/device/report')
def device_report():
    mac_addr = request.form.get('mac_addr')
    device = Device.get_by_mac_addr(mac_addr)
    if not device:
        raise exceptions.NotFound(description=f'device witch mac_addr {mac_addr} not found.')

    reported_fields = {}
    allowed_report_fields = ['mac_addr', 'ipv4_addr', 'ipv6_addr', 'protocol', 'port',
                             'sync_mode', 'report_interval', 'attrs']
    for field, target in request.form.items():
        if field in allowed_report_fields:
            reported_fields[field] = target
        else:
            raise exceptions.BadRequest(description=f'Field {field} is not allowed to be reported.')

    try:
        device.update(reported_fields)
        device.online()
        device.save()
    except ValidationError as e:
        error_msg = ''.join([f'{error["loc"][0]}: {error["msg"]}' for error in e.errors()])
        raise exceptions.BadRequest(description=error_msg)

    return device_view(device, exclude_keys=['attrs'])
