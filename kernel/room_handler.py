""" RoomHandler
    Add room
    del room
    get room_list
    build roomDict
"""
import os
import copy
import json
import shutil
from common.constants import ROOM_PATH
from common.constants import MY_DEVICES
from kernel.file_handler import save_room_list_to_file
from kernel.file_handler import get_room_list_from_file
from kernel.file_handler import save_room_content_to_file
from kernel.file_handler import get_room_content_from_file
from kernel.file_handler import build_new_room_content_dict


class RoomHandler:
    """ RoomHandler.class
        Handle all about room
        and just about room
    """
    def __init__(self):
        self.__room_name_map_room_content = dict()
        room_list = get_room_list_from_file()
        for room in room_list:
            room_content = get_room_content_from_file(room['name'])
            # All room content in roomContentListDict
            # and set all devices' status to True
            # and iot_manager would check it's status
            self.__room_name_map_room_content[room['name']] = room_content
            for index in range(len(room_content['devices'])):
                room_content['devices'][index]['status'] = False

        # for Unauthorized devices
        if not self.get_room_content(MY_DEVICES):
            print(self.add_room(MY_DEVICES))

    def add_room(self, room_name):
        """ Add new room to room_list,
            and create a new folder for the room,
            and create a .roomContentFile to record all devices of the room

            return room_list which dumps by json
        """
        if os.path.exists(ROOM_PATH + room_name):
            return 'Room already exists.'
        # Add new folder and initial
        os.makedirs(ROOM_PATH + room_name)
        room_content = build_new_room_content_dict(room_name)
        save_room_content_to_file(room_content)
        # Add new room information to iot_manager's room_content_list_dict
        if not self.__room_name_map_room_content.get(room_name):
            self.__room_name_map_room_content[room_name] = room_content
        save_room_list_to_file(self.get_room_list())

        return self.get_room_json_list()

    def delete_room(self, room_name):
        """ Delete a room from room_list,
            and delete the folder of the room
        """
        if os.path.exists(ROOM_PATH + room_name):
            # delete the folder of the room
            shutil.rmtree(ROOM_PATH + room_name)
            # delete room from roomContentListDict
            if self.__room_name_map_room_content.get(room_name):
                self.__room_name_map_room_content.pop(room_name)
                save_room_list_to_file(self.get_room_list())
        return 'Delete room succeed'

    def rename_room(self, old_room_name, new_room_name):
        """ Rename the folder of the room
            Rename Key of self.__roomContentListDict
        """
        if os.path.exists(ROOM_PATH + old_room_name):
            if not os.path.exists(ROOM_PATH + new_room_name):
                # rename folder
                shutil.move(ROOM_PATH + old_room_name, ROOM_PATH + new_room_name)
                room_content = self.__room_name_map_room_content[old_room_name]
                room_content['name'] = new_room_name
                self.__room_name_map_room_content[new_room_name] = room_content
                save_room_content_to_file(room_content)
                self.__room_name_map_room_content.pop(old_room_name)
                save_room_list_to_file(self.get_room_list())

    def get_room_json_list(self):
        """ get room list which dumps by json"""
        room_list = self.get_room_list()
        return json.dumps(room_list)

    # basic functions
    def get_room_content(self, room_name):
        """ room content getter """
        return self.__room_name_map_room_content.get(room_name)

    def get_room_content_list_dict(self):
        return self.__room_name_map_room_content

    def get_room_list(self):
        """ room list getter """
        room_list = copy.deepcopy(list(self.__room_name_map_room_content.values()))
        # room_list don't need devices' information
        for index in range(len(room_list)):
            room_list[index]['devices'] = []
        return room_list

    def save_room_list_and_room_content_to_file(self):
        """ save room list and room content to file at regular time """
        # save room list
        save_room_list_to_file(self.get_room_list())

        room_content_list = list(self.__room_name_map_room_content.values())
        for room_content in room_content_list:
            save_room_content_to_file(room_content)
        print('Save finished.')
