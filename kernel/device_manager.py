'''DeviceHandler
   Add device
   del device
   move device
   rename device
'''
import os
import json
import time
import shutil
import platform
import importlib
import threading
import subprocess
from kernel.file_handler import save_room_content_to_file
from common.constants import MY_DEVICES
from common.constants import ROOM_PATH


class DeviceHandler(object):
    """
    DeviceHandler is responsible for add a new device to access in raspIot,
    and get a json contains device attribute for onLineIotServerListDict by device's uuid,
    and set device content to a new value, means control iot devices.
    and check those online devices is still aliving or not in a child thread,
    and setup iotServer in a child thread when a iot device access in.

    Attributes:
        All is private
    """
    ping_cmd = None  # for check device alive

    def __init__(self, iot_manager):
        """ DeviceHandler initial
        Args:
            iot_manager: this object is one attribute of the iot_manager

        Returns:
            None
        """
        self.IotManager = iot_manager
        self.__device_uuid_map_iot_server = dict()
        self.__devices_uuid_map_room = dict()
        room_content_list = list(self.IotManager.room_handler.get_room_content_list_dict().values())
        for room_content in room_content_list:
            for index in range(len(room_content['devices'])):
                # using uuid to map room, make room search faster
                deviceUuid = room_content['devices'][index]['uuid']
                self.__devices_uuid_map_room[deviceUuid] = room_content['name']
        threading.Thread(target=self.check_is_iot_device_aliving, args=()).start()

    def add_device(self, room_name, device):
        """ add_device method
        Args:
            room_name: the name of the room which new device belong to.
            device: a dict instance that include all informations of the new device.

        Returns:
            A str contains the result of add device succeed or not.
            'Device already exists.' or 'Add device succeed.'
        """
        device_uuid = device['uuid'].upper()
        check_room_name = self.__devices_uuid_map_room.get(device_uuid)
        if check_room_name and check_room_name != MY_DEVICES:
            return 'Device already exists.'
        self.__devices_uuid_map_room[device_uuid] = room_name
        room = self.IotManager.room_handler.get_room_content(room_name)
        room['devices'].append(device)
        save_room_content_to_file(room)
        return 'Add device succeed.'

    def rename_device(self, device_uuid, new_device_name):
        """rename_device method
        Args:
            device_uuid
            new_device_name
        """
        iot_server = self.__device_uuid_map_iot_server.get(device_uuid)
        if iot_server:
            iot_server.name = new_device_name
        room_name = self.__devices_uuid_map_room.get(device_uuid)
        if room_name:
            room_handler = self.IotManager.get_room_handler()
            room_content = room_handler.get_room_content(room_name)
            for index in range(len(room_content['devices'])):
                if room_content['devices'][index]['uuid'] == device_uuid:
                    room_content['devices'][index]['name'] = new_device_name
                    save_room_content_to_file(room_content)
                    break

    def move_device(self, device_uuid, new_room_name):
        """ move_device method
        Args:
            device_uuid: uuid of the device which need to move
            new_room_name: the new room that device will move to
        """
        room_name = self.__devices_uuid_map_room.get(device_uuid)
        if room_name:
            room_content = self.IotManager.room_handler.get_room_content(room_name)
            for index in range(len(room_content['devices'])):
                print(room_content['devices'][index])
                if device_uuid == room_content['devices'][index]['uuid']:
                    device = room_content['devices'][index]
                    self.__devices_uuid_map_room.pop(device_uuid)
                    if self.add_device(new_room_name, device) == 'Add device succeed.':
                        room_content['devices'].remove(device)
                        save_room_content_to_file(room_content)
                    else:
                        self.__devices_uuid_map_room[device_uuid] = room_name
                    break

    def move_all_device(self, old_room_name, new_room_name):
        """move_all_device method
        Args:
            :param old_room_name: room name of devices those need to move
            :param new_room_name: the new room that devices will move to
        """
        room_content = self.IotManager.room_handler.get_room_content(old_room_name)
        if room_content:
            for d in room_content['devices']:
                self.move_device(d['uuid'], new_room_name)

    def delete_device(self, device_uuid):
        """ delete_device method
        Args:
            device_uuid: uuid of the device which will be delete
        """
        room_name = self.__devices_uuid_map_room.get(device_uuid)
        if room_name:
            room_content = self.IotManager.room_handler.get_room_content(room_name)
            for index in range(len(room_content['devices'])):
                print(room_content['devices'][index])
                if device_uuid == room_content['devices'][index]['uuid']:
                    device = room_content['devices'][index]
                    self.__devices_uuid_map_room.pop(device_uuid)
                    room_content['devices'].remove(device)
                    save_room_content_to_file(room_content)
                    break

    def get_device_attribute_by_uuid(self, uuid):
        """getDeviceJsonByUuid method
        Args:
            uuid: uuid of the device which you want to get it's device attribute

        Returns:
            a dict of device's attribute
        """
        if self.__device_uuid_map_iot_server.get(uuid) is None:
            return None
        iot_server = self.__device_uuid_map_iot_server.get(uuid)
        try:
            attribute = iot_server.get_device_attribute()
        except Exception:
            attribute = None
        return attribute

    def set_value_to_device_content(self, room_name, device_name, device_content_name, value):
        """set_value_to_device_content method
        Args:
            room_name: a str representing the name of the room that the device belong to
            device_name: a str representing the name of the device content that want to send new value
            device_content_name: a str representing the name that need to set new value
            value: a str of new value

        Returns:
            a str representing the value of the device content after set new value

        Raises:
            AttributeError: an error occurred accessing the iot_server.get_device_attribute() method.
            KeyError: an error occurred accessing deviceContent's 'setter' Key.
        """
        try:
            room = self.IotManager.room_handler.get_room_content(room_name)
            for index in range(len(room['devices'])):
                if room['devices'][index]['name'] == device_name:
                    device_uuid = room['devices'][index]['uuid']
                    break

            iot_server = self.__device_uuid_map_iot_server[device_uuid]
            device = iot_server.get_device_attribute()
            for index in range(len(device['deviceContent'])):
                if device['deviceContent'][index]['name'] == device_content_name:
                    device_content_setter = device['deviceContent'][index]['setter']
                    break

            exec('iot_server.' + device_content_setter + '("' + value + '")')
        except Exception as reason:
            print(__file__ + " Error: " + str(reason))
            return "false"
        return "true"

    def check_is_iot_device_aliving(self):
        """ check_is_iot_device_aliving method
        At regularly time, ping all the iot device to check iot devices is Aliving or not
        and it should work in a child thread, because it will always work.

        Args:
            None

        Raisers:
            TypeError: an error occurred accessing ping result in not utf-8 encoding
        """
        sys_type = platform.system()
        if sys_type == 'Windows':
            DeviceHandler.ping_cmd = 'ping -n 3 '
        elif sys_type == 'Linux':
            DeviceHandler.ping_cmd = 'ping -c 3 '
        while True:
            time.sleep(10)  # 10 seconds
            for iotServer in list(self.__device_uuid_map_iot_server.values()):
                try:
                    device_ip = iotServer.ip
                    device_uuid = iotServer.uuid
                    if self.ping_device(device_ip) is False:
                        del iotServer  # device unreachable, shut iotServer down
                        self.__device_uuid_map_iot_server.pop(device_uuid)  # iotServer offline
                        room_name = self.__devices_uuid_map_room[device_uuid]
                        room_content = self.IotManager.room_handler.get_room_content(room_name)
                        for index in range(len(room_content['devices'])):
                            if room_content['devices'][index]['uuid'] == device_uuid:
                                # set iotServer status to offline
                                room_content['devices'][index]['status'] = False
                                print(room_name + ': ' + room_content['devices'][index]['name'] + ' offline')
                                break
                        save_room_content_to_file(room_content)
                except Exception as reason:
                    print(str(reason))
                    # End threading
                    return

    @staticmethod
    def ping_device(device_ip):
        if device_ip is None:
            return False
        ping_cmd = DeviceHandler.ping_cmd + device_ip
        try:
            subprocess.check_output(ping_cmd, shell=True)
            return True
        # device unreachable
        except subprocess.CalledProcessError:
            return False

    def setup_iot_server(self, conn, recvdata):
        """ setup_iot_server method
        Setup IotServer in a new thread when iot device access in.
        """
        threading.Thread(target=self.iot_server_setter, args=(conn, recvdata)).start()

    def iot_server_setter(self, conn, recv_data):
        """ iot_server_setter method
        Parser recvdata that from iot device to get ip, uuid, iotServer module, repository, etc.
        Get iotServer module from repository, and set it up, and add it to onlineIotServerListDict.

        Args:
            conn: a connect from iot device
            recv_data: a dict contains device's information. For example:{"uuid":"5c:cf:7f:14:73:ab",
                                                                         "repository":"raspIot",
                                                                         "device":"ds18b20",
                                                                         "iotServer":"DS18B20",
                                                                         "identity":"device",
                                                                         "ip":"192.168.17.138"}
        Returns:
            None. But it will reply the result of setup iotServer to the device by conn.

        Raises:
            KeyError: an error occurred accessing recvdata's Key.
        """
        ip = recv_data['ip']
        uuid = recv_data['uuid'].upper()
        module_name = class_name = recv_data['iotServer']

        if not self.__devices_uuid_map_room.get(uuid):
            # No UNAUTHORIZED_ACCESS_MODE: reject
            conn.sendall(json.dumps({'response': 'Setup completed'}).encode())  # for the moment
            print('Unauthorized devices: ' + uuid + ' is rejected to access in.')
            conn.close()
            # save information of the unauthorized device
            device_name = recv_data['device'] + '_' + uuid.replace(':', '')[-4:]
            device_info = build_new_device_dict(device_name, uuid)
            msg = "An unauthorized device try to access in.\nThis is its information: " + str(device_info)
            print(msg)
            print("Finished.")
            return
        else:
            # search which room it's belong to
            room_name = self.__devices_uuid_map_room[uuid]
            device_name = self.get_device_name_by_uuid(uuid)
        try:
            # get iotServer module from device's server
            iot_server_file = module_name + '.py'
            iot_server_path = ROOM_PATH + room_name + '/' + iot_server_file
            if not os.path.exists(iot_server_path):
                shutil.copyfile('devices/server/' + iot_server_file, iot_server_path)
            # import module from IotServer/
            iot_server_module = importlib.import_module('rooms.' + room_name + '.' + module_name)
            # import class from module
            iot_server_class = getattr(iot_server_module, class_name)

            # instantiation
            iot_server = iot_server_class(ip, uuid, device_name)
            if not self.__device_uuid_map_iot_server.get(uuid):
                self.__device_uuid_map_iot_server[uuid] = iot_server

            if room_name == MY_DEVICES:
                device_dict = build_new_device_dict(device_name, uuid)
                device_dict['status'] = True

            # set status of this iotServer True
            devices = self.IotManager.room_handler.get_room_content(room_name)['devices']

            for index in range(len(devices)):
                if devices[index]['uuid'] == uuid:
                    devices[index]['status'] = True
                    print(room_name + ': ' + devices[index]['name'] + ' online')
                    break
            conn.sendall(json.dumps({'response': 'Setup completed'}).encode())
            print("Finished.")
            conn.close()
        except Exception as reason:
            print(__name__ + ' Error: ' + str(reason))

    def get_device_uuid_by_name(self, room_name, device_name):
        room_handler = self.IotManager.get_room_handler()
        room_content = room_handler.get_room_content(room_name)
        if room_content:
            for d in room_content['devices']:
                if d['name'] == device_name:
                    return d['uuid']

    def get_device_name_by_uuid(self, uuid):
        room_name = self.__devices_uuid_map_room[uuid]
        room = self.IotManager.room_handler.get_room_content(room_name)
        try:
            devices = room['devices']
            for index in range(len(devices)):
                if devices[index]['uuid'] == uuid:
                    deviceName = devices[index]['name']
                    return deviceName
        except Exception:
            return None

    def get_device_ip_by_uuid(self, uuid):
        iot_server = self.__device_uuid_map_iot_server.get(uuid)
        if iot_server is not None:
            return iot_server.ip
        else:
            return None


def build_new_device_dict(device_name, device_uuid):
    """ build_new_device_dict function
    Build a device by a blueprint of device attribute

    Args:
        device_name: a str representing name of the device.
        device_uuid: a str representing uuid of the device.

    Returns:
        device_dict: a dict of device attribute
    """
    device_dict = {"name": device_name,
                   "uuid": device_uuid,
                   "status": False}
    return device_dict
