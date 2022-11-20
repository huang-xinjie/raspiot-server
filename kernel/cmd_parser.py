"""cmd_parser.py
Parser cmd that from app
"""
import copy
import json
import datetime
from kernel.device_manager import build_new_device_dict
from common.constants import DEFAULT_IDENTITY
from common.constants import MY_DEVICES
from config.user import ACCOUNT


class CmdParser:
    """CmdParser class
    parse cmd from app and return result to app
    """

    def __init__(self, iot_manager):
        self.iot_manager = iot_manager

    def set_command(self, conn, target, value):
        target = target.split(':')
        room_handler = self.iot_manager.get_room_handler()
        device_handler = self.iot_manager.get_device_handler()
        if target[0] == 'room':  # room rename
            old, new = target[1], value
            room_handler.rename_room(old, new)
            device_handler.move_all_device(old, new)
            conn.sendall('Rename succeed.'.encode())
        elif target[0] == 'device':
            old_room, device_name = target[1].split('/')
            new_room, new_device_name = value.split('/')
            device_uuid = device_handler.get_device_uuid_by_name(old_room, device_name)
            if old_room == new_room:  # device rename
                device_handler.rename_device(device_uuid, new_device_name)
            else:  # device move
                device_handler.move_device(device_uuid, new_room)
        elif target[0] == 'deviceContent':  # set deviceContent to new value
            room_name, device_name, device_content_name = target[1].split('/')
            result = device_handler.set_value_to_device_content(room_name, device_name, device_content_name, value)
            conn.sendall(result.encode())

    def get_command(self, conn, target, value):
        target = target.split(':')
        if target[0] == 'server' and value == 'checkServices':  # check services
            conn.sendall("raspServer is ready.".encode())
        elif target[0] == 'room' and value == 'roomlist':  # get room list
            room_handler = self.iot_manager.get_room_handler()
            conn.sendall(room_handler.get_room_json_list().encode())
        elif target[0] == 'device' and value == 'devicelist':  # get device list
            send_json = self.build_json(target[1])
            conn.sendall(send_json.encode())

    def add_command(self, conn, target, value):
        target = target.split(':')
        if target[0] == 'room':  # add a new room
            room_name = value
            room_handler = self.iot_manager.get_room_handler()
            conn.sendall(room_handler.add_room(room_name).encode())
        elif target[0] == 'device':  # add a new device
            device_uuid = value
            room_name, deviceName = target[1].split('/')
            device_dict = build_new_device_dict(deviceName, device_uuid)
            device_handler = self.iot_manager.get_device_handler()
            conn.sendall(device_handler.add_device(room_name, device_dict).encode())

    def del_command(self, conn, target, value):
        device_handler = self.iot_manager.get_device_handler()
        if target.split(':')[0] == 'room':  # delete a room from home
            room_name = value
            device_handler.move_all_device(room_name, MY_DEVICES)
            conn.sendall('Done'.encode())
            room_handler = self.iot_manager.get_room_handler()
            room_handler.delete_room(room_name)

        # delete a device from room and move to Unauthorized_devices
        elif target.split(':')[0] == 'device':
            room_name, device_name = target.split(':')[1], value
            device_uuid = device_handler.get_device_uuid_by_name(room_name, device_name)
            device_handler.delete_device(device_uuid)

    def command_parser(self, conn, recvdata):
        if recvdata['identity'] == ACCOUNT or recvdata['identity'] == DEFAULT_IDENTITY:
            cmd, target, value = recvdata['cmd'], recvdata['target'], recvdata['value']
            if cmd == "get":
                self.get_command(conn, target, value)
            elif cmd == 'set':
                self.set_command(conn, target, value)
            elif cmd == 'add':
                self.add_command(conn, target, value)
            elif cmd == 'del':
                self.del_command(conn, target, value)
            print("Finished.")
            conn.close()
        elif recvdata['identity'] == 'device':
            self.iot_manager.device_handler.setup_iot_server(conn, recvdata)

    def build_json(self, room_name):
        device_list = []
        device_handler = self.iot_manager.get_device_handler()
        room_content = copy.deepcopy(self.iot_manager.room_handler.get_room_content(room_name))
        if not room_content:
            return json.dumps([])
        for d in room_content['devices']:
            if d['status']:
                device_attribute = device_handler.get_device_attribute_by_uuid(d['uuid'])
                # pop key: 'getter' or 'setter'
                if device_attribute:
                    for deviceContent in device_attribute['deviceContent']:
                        if deviceContent.get('getter'):
                            deviceContent.pop('getter')
                        elif deviceContent.get('setter'):
                            deviceContent.pop('setter')
                    device_attribute['status'] = True
                    device_list.append(device_attribute)
                    continue

            # elif not d['status']:
            d['status'] = False
            d['deviceContent'] = []
            device_list.append(d)

        room_details = {'name': room_name,
                        'updateTime': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'devices': device_list}

        return json.dumps(room_details)
