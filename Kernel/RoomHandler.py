''' RoomHandler
    Add room
    del room
    get roomList
    build roomDict
'''
import os
import json
import time
import shutil
import threading
from Kernel.GlobalConstant import ROOM_PATH
from Kernel.FileHandler import saveRoomListToFile
from Kernel.FileHandler import getRoomListFromFile
from Kernel.FileHandler import saveRoomContentToFile
from Kernel.FileHandler import getRoomContentFromFile
from Kernel.FileHandler import buildNewRoomContentDict



class RoomHandler:
    ''' RoomHandler.class
        Handle all about room
    '''
    # private
    __roomContentListDict = dict()

    def __init__(self):
        roomList = getRoomListFromFile()
        for room in roomList:
            roomContent = getRoomContentFromFile(room['name'])
            # All room content in roomContentListDict and set all devices' status to False
            self.__roomContentListDict[room['name']] = roomContent
            for index in range(len(roomContent['devices'])):
                roomContent['devices'][index]['status'] = False
        threading.Thread(target=self.saveRoomListAndRoomContentToFileRegularly, args=()).start()

    def addRoom(self, roomName):
        '''
            Add new room to roomList,
            and create a new folder for the room,
            and create a .roomContentFile to record all devices of the room

            return roomList which dumps by json
        '''
        if os.path.exists(ROOM_PATH + roomName):
            return 'Room already exists.'
        # Add new folder and initial
        os.makedirs(ROOM_PATH + roomName)
        saveRoomContentToFile(buildNewRoomContentDict(roomName))
        # Add new room information to IotManager's roomContentListDict
        roomContent = buildNewRoomContentDict(roomName)
        if self.__roomContentListDict.get(roomName) is None:
            self.__roomContentListDict[roomName] = roomContent
        saveRoomListToFile(self.getRoomList())

        return self.getRoomJsonList()


    def delRoom(self, roomName):
        '''
            Delete a room from roomList,
            and delete the folder of the room
        '''
        if os.path.exists(ROOM_PATH + roomName):
            # delete the folder of the room
            shutil.rmtree(ROOM_PATH + roomName)
            # delete room from roomContentListDict
            if self.__roomContentListDict.get(roomName) is not None:
                self.__roomContentListDict.pop(roomName)
        return self.getRoomJsonList()

    def getRoomJsonList(self):
        ''' get room list which dumps by json'''
        roomList = self.getRoomList()
        return json.dumps(roomList)


    def getRoomContent(self, roomName):
        ''' room content getter '''
        return self.__roomContentListDict[roomName]

    def getRoomContentListDict(self):
        return self.__roomContentListDict


    def getRoomList(self):
        ''' room list getter '''
        roomList = list(self.__roomContentListDict.values())
        # roomList don't need devices' information
        for index in range(len(roomList)):
            roomList[index]['devices'] = []
        return roomList


    def saveRoomListAndRoomContentToFileRegularly(self):
        ''' save room list and room content to file at regular time '''
        while True:
            # hold it for three minutes
            time.sleep(3 * 60)
            # save room list
            saveRoomListToFile(self.getRoomList())
            # remove device's status before save

            roomContentList = list(self.__roomContentListDict.values())
            for roomContent in roomContentList:
                saveRoomContentToFile(roomContent)
            print('Auto save finished.')
