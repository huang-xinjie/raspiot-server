'''IotManager.py
    Manage IotServer and IotDevice
    Including access IotDevice and setup IotServer
'''

import os
import json
import time
import shutil
import importlib
import threading
from Kernel.CmdParser import CmdParser
from Kernel.RoomHandler import RoomHandler
from Kernel.FileHandler import saveRoomListToFile
from Kernel.FileHandler import getRoomListFromFile
from Kernel.FileHandler import saveRoomContentToFile
from Kernel.FileHandler import getRoomContentFromFile


class IotManager:
    '''IotManager.class
        Manage IotServer and IotDevice
        Including access IotDevice and setup IotServer
    '''

    roomList = list()
    devicesUuidMapRoom = dict()
    roomContentListDict = dict()

    def __init__(self):
        # set a cmdParser for iotManager
        self.cmdParser = CmdParser(self)
        # set a roomHandler for iotManager
        self.roomHandler = RoomHandler(self)
        self.roomList = getRoomListFromFile()
        for room in self.roomList:
            self.buildRoomContentVariable(room['name'])
        threading.Thread(target=self.saveRoomListAndRoomContentToFileRegularly, args=()).start()


    def buildRoomContentVariable(self, roomName):
        ''' Get room content from folder and build variable '''
        roomContent = getRoomContentFromFile(roomName)
        # All room content in roomContentList
        self.roomContentListDict[roomName] = roomContent
        for index in range(len(roomContent['devices'])):
            roomContent['devices'][index]['status'] = False
            # using uuid to map room, make room search faster
            deviceUuid = roomContent['devices'][index]['uuid']
            self.devicesUuidMapRoom[deviceUuid] = roomName

        # use every different room name to build variable
        # format: _roomname_RoomContent
        # setattr(self, self.buildRoomVariableName(roomName), roomContent)


    # def buildRoomVariableName(self, roomName):
    #    ''' format: _roomname_RoomContent '''
    #    return '_' + roomName + '_RoomContent'


    def getRoomList(self):
        ''' room list getter '''
        return self.roomList

    def getRoomHandler(self):
        ''' room handler getter '''
        return self.roomHandler

    def getCmdParser(self):
        ''' cmd parser getter '''
        return self.cmdParser

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
            # search which room it's belong to
            roomName = self.devicesUuidMapRoom['uuid']
            # set status of this iotServer True

            for index in range(len(self.roomContentListDict[roomName]['devices'])):
                if self.roomContentListDict[roomName][index]['uuid'] == mac:
                    self.roomContentListDict[roomName][index]['status'] = True
                    break

            conn.sendall(json.dumps({'response':'Setup completed'}).encode())
            # exec('print(iotServerList[0].' + iotServerList[0].buildDeviceJSON()['deviceContent'][0]['getter'] + ')')
        except Exception as reason:
            print(__file__ +' Error: ' + str(reason))


    def saveRoomListAndRoomContentToFileRegularly(self):
        ''' save room list and room content to file at regular time '''
        while True:
            # hold it for three minutes
            time.sleep(3 * 60)
            # save room list
            saveRoomListToFile(self.roomList)
            # remove device's status before save
            for roomContent in self.roomContentListDict:
                saveRoomContentToFile(roomContent)
