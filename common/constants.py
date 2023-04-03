"""constants.py
    All Global Constant in here
"""
from datetime import datetime


# socket sendall or recv max buffsize
BUFF_SIZE = 2048

# Room path
ROOM_PATH = 'rooms/'

# raspiot standard initial time
STANDARD_INITIAL_TIME = datetime.strptime("2015-12-17 22:22:00.000022", '%Y-%m-%d %H:%M:%S.%f')

# path of room list file
ROOM_LIST_FILE = ROOM_PATH + '.room_list_file.pkl'

MY_DEVICES = 'my_devices'

DEFAULT_IDENTITY = "support@raspiot.org"
