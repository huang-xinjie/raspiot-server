'''IotManager.py
    Manage IotServer and IotDevice
    Including access IotDevice and setup IotServer
'''

import os
import json
import shutil
import importlib
import threading
from Kernel.CmdParser import CmdParser
from Kernel.RoomHandler import RoomHandler
from Kernel.DeviceHandler import DeviceHandler


class IotManager:
    '''IotManager.class
        Manage IotServer and IotDevice
        Including access IotDevice and setup IotServer
    '''
    devicesUuidMapRoom = dict()

    def __init__(self):
        # set a cmdParser for iotManager
        self.cmdParser = CmdParser(self)
        # set a roomHandler for iotManager
        self.roomHandler = RoomHandler()
        roomContentList = list(self.roomHandler.getRoomContentListDict().values())
        for roomContent in roomContentList:
            for index in range(len(roomContent)):
                # using uuid to map room, make room search faster
                deviceUuid = roomContent['devices'][index]['uuid']
                self.devicesUuidMapRoom[deviceUuid] = roomContent['name']
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


    def setupIotServer(self, conn, recvdata):
        ''' Setup IotServer in a new thread '''
        threading.Thread(target=self.IotServerSetter, args=(conn, recvdata)).start()


    def IotServerSetter(self, conn, recvdata):
        ''' setup IotServer and add it to iotServerList '''
        ip = recvdata['ip']
        mac = recvdata['mac']
        moduleName = className = recvdata['iotServer']
        
        try:
            if os.path.exists('IotServer/' + moduleName + '.py') is False:

                shutil.copyfile('Repository/' + moduleName + '.py', 'IotServer/' + moduleName + '.py')
            # import module from IotServer/
            iotServerModule = importlib.import_module('IotServer.' + moduleName)
            # import class from module
            iotServerClass = getattr(iotServerModule, className)
            # instantiation
            iotServer = iotServerClass(ip, mac)

            conn.sendall(json.dumps({'response':'Setup completed'}).encode())

            # search which room it's belong to
            roomName = self.devicesUuidMapRoom['uuid']
            # set status of this iotServer True
            '''
            for index in range(len(self.roomContentListDict[roomName]['devices'])):
                if self.roomContentListDict[roomName][index]['uuid'] == mac:
                    self.roomContentListDict[roomName][index]['status'] = True
                    break
            '''
            conn.sendall(json.dumps({'response':'Setup completed'}).encode())
            # exec('print(iotServerList[0].' + iotServerList[0].buildDeviceJSON()['deviceContent'][0]['getter'] + ')')
        except Exception as reason:
            print(__file__ +' Error: ' + str(reason))
