"""iot_manager.py
    Manage IotServer and IotDevice
    Including access IotDevice and setup IotServer
"""

from kernel.cmd_parser import CmdParser
from kernel.room_handler import RoomHandler
from kernel.device_manager import DeviceHandler


class IotManager:
    """iot_manager.class
        Manage IotServer and IotDevice
        Including access IotDevice and setup IotServer
    """

    def __init__(self):
        # set a cmdParser for iot_manager
        self.cmd_parser = CmdParser(self)
        # set a roomHandler for iot_manager
        self.room_handler = RoomHandler()
        # set a deviceHandler for iot_manager
        self.device_handler = DeviceHandler(self)

    def get_cmd_parser(self):
        """ cmd parser getter """
        return self.cmd_parser

    def get_room_handler(self):
        """ room handler getter """
        return self.room_handler

    def get_device_handler(self):
        """ device handler getter """
        return self.device_handler
