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
from RoomHandler import getRoomListFromFile, saveRoomListToFile, saveRoomContentToFile, getRoomContentFromFile


class IotManager:
    '''IotManager.class
        Manage IotServer and IotDevice
        Including access IotDevice and setup IotServer
    '''

    roomList = list()
    roomContentList = list()

    def __init__(self):
        self.roomList = getRoomListFromFile()
        for room in self.roomList:
            self.buildRoomContentVariable(room['name'])
        threading.Thread(target=self.saveRoomListAndRoomContentToFileAtRegularTime, args=None)

    def buildRoomContentVariable(self, roomName):
        ''' Get room content from folder and build variable '''
        roomContent = getRoomContentFromFile(roomName)
        self.roomContentList.append(roomContent)
        for index in range(len(roomContent['devices'])):
            roomContent['devices'][index]['status'] = False
        # use every different room name to build variable   format: _roomname_RoomContent
        setattr(self, '_' + roomName + '_RoomContent', roomContent)



    def setupIotServer(self, conn, recvdata):
        ''' Setup IotServer in a new thread '''
        threading.Thread(target=self.IotServerSetter, args=(conn, recvdata))


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
            #exec('print(iotServerList[0].' + iotServerList[0].buildDeviceJSON()['deviceContent'][0]['getter'] + ')')
        except Exception as reason:
            print(__file__ +' Error: ' + str(reason))

    
    def saveRoomListAndRoomContentToFileAtRegularTime(self):
        ''' save room list and room content to file at regular time '''
        while True:
            # hold it for five minutes
            time.sleep(5 * 60)
            # save room list
            saveRoomListToFile(self.roomList)
            # remove device's status before save
            for roomContent in self.roomContentList:
                for index in range(len(roomContent['devices'])):
                    roomContent['devices'][index].pop('status')
                saveRoomContentToFile(roomContent)
