'''IotManager.py
    Manage IotServer and IotDevice
    Including access IotDevice and setup IotServer
'''

from Kernel.CmdParser import CmdParser
from Kernel.RoomHandler import RoomHandler
from Kernel.DeviceHandler import DeviceHandler


class IotManager:
    '''IotManager.class
        Manage IotServer and IotDevice
        Including access IotDevice and setup IotServer
    '''


    def __init__(self):
        # set a cmdParser for iotManager
        self.cmdParser = CmdParser(self)
        # set a roomHandler for iotManager
        self.roomHandler = RoomHandler()
        # set a deviceHandler for iotManager
        self.deviceHandler = DeviceHandler(self)


    def getCmdParser(self):
        ''' cmd parser getter '''
        return self.cmdParser

    def getRoomHandler(self):
        ''' room handler getter '''
        return self.roomHandler

    def getDeviceHandler(self):
        ''' device handler getter '''
        return self.deviceHandler
