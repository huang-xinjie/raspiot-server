from flask import jsonify

from objects.device import DeviceAttrType


def _attrs_view(attr_obj_list, exclude_keys=None):
    attr_list = []
    for attr_obj in attr_obj_list:
        attr_type = attr_obj.get('type')
        attr_value = attr_obj.get('value', '')
        if attr_type == DeviceAttrType.switch and not isinstance(attr_value, bool):
            attr_value = bool(attr_value.lower() in ['1', 'true'])
        attr = dict(name=attr_obj.get('name'),
                    type=attr_type,
                    value=attr_value,
                    read_only=attr_obj.get('read_only'),
                    value_constraint=attr_obj.get('value_constraint'))
        attr_list.append(attr)

    return attr_list


def device_view(device_obj, exclude_keys=None):
    device_dict = dict(uuid=device_obj.get('uuid'),
                       name=device_obj.get('name'),
                       status=device_obj.get('status'),
                       mac_addr=device_obj.get('mac_addr'),
                       ipv4_addr=device_obj.get('ipv4_addr'),
                       ipv6_addr=device_obj.get('ipv6_addr'),
                       protocol=device_obj.get('protocol'),
                       port=device_obj.get('port'),
                       sync_mode=device_obj.get('sync_mode'),
                       sync_interval=device_obj.get('sync_interval'),
                       attrs=_attrs_view(device_obj.get('attrs')),
                       synced_at=str(device_obj.get('synced_at')),
                       created_at=str(device_obj.get('created_at')))

    if exclude_keys:
        [device_dict.pop(k, None) for k in exclude_keys]

    return device_dict


def device_list_view(device_obj_list, exclude_keys=None):
    device_list = []
    for device_obj in device_obj_list:
        device_list.append(device_view(device_obj, exclude_keys))

    return jsonify(device_list)
