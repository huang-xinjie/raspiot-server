"""file_handler.py

"""
import os
import pickle
from common.constants import ROOM_PATH
from common.constants import ROOM_LIST_FILE
from common.constants import STANDARD_INITIAL_TIME


def get_room_list_from_file():
    """ get room list form .roomListFile.pkl """
    if not os.path.exists(ROOM_LIST_FILE):
        save_room_list_to_file([])
    with open(ROOM_LIST_FILE, 'rb') as roomListFileRb:
        room_list = pickle.load(roomListFileRb)
    return room_list


def save_room_list_to_file(room_list):
    """ save room list to rooms/.roomListFile.pkl """
    with open(ROOM_LIST_FILE, 'wb') as roomListFileWb:
        pickle.dump(room_list, roomListFileWb)


def get_room_content_from_file(room_name):
    """ get room content from rooms/<room_name>/.room_content_file.pkl """
    room_content_file = ROOM_PATH + room_name + '/.room_content_file.pkl'
    if not os.path.exists(room_content_file):
        save_room_content_to_file(build_new_room_content_dict(room_name))
    with open(room_content_file, 'rb') as roomContentFileRb:
        room_content = pickle.load(roomContentFileRb)
    return room_content


def save_room_content_to_file(room_content):
    """ save room content to  rooms/<room_name>/.room_content_file.pkl """
    room_content_file = ROOM_PATH + room_content['name'] + '/.room_content_file.pkl'
    if not os.path.exists(ROOM_PATH + room_content['name']):
        os.makedirs(ROOM_PATH + room_content['name'])
    with open(room_content_file, 'wb') as roomContentFileWb:
        pickle.dump(room_content, roomContentFileWb)


def build_new_room_content_dict(room_name):
    """ build a room content by room content blueprint """
    room_content_dict = {"name": room_name,
                         "updateTime": STANDARD_INITIAL_TIME,
                         "devices": []}
    return room_content_dict
