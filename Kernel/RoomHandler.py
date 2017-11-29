''' RoomHandler
    Add room
    del room
    get roomList
    build roomDict
'''
import os
import copy
import json
import shutil
from Kernel.GlobalConstant import ROOM_PATH
from Kernel.GlobalConstant import Ungrouped_devices
from Kernel.FileHandler import saveRoomListToFile
from Kernel.FileHandler import getRoomListFromFile
from Kernel.FileHandler import saveRoomContentToFile
from Kernel.FileHandler import getRoomContentFromFile
from Kernel.FileHandler import buildNewRoomContentDict



class RoomHandler:
    ''' RoomHandler.class
        Handle all about room
        and just about room
    '''
    # private
    __roomNameMapRoomContent = dict()

    def __init__(self):
        roomList = getRoomListFromFile()
        for room in roomList:
            roomContent = getRoomContentFromFile(room['name'])
            # All room content in roomContentListDict
            # and set all devices' status to True
            # and iotManager would check it's status
            self.__roomNameMapRoomContent[room['name']] = roomContent
            for index in range(len(roomContent['devices'])):
                roomContent['devices'][index]['status'] = True

        # for Unauthorized devices
        if not self.getRoomContent(Ungrouped_devices):
            print(self.addRoom(Ungrouped_devices))

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
        roomContent = buildNewRoomContentDict(roomName)
        saveRoomContentToFile(roomContent)
        # Add new room information to IotManager's roomContentListDict
        if not self.__roomNameMapRoomContent.get(roomName):
            self.__roomNameMapRoomContent[roomName] = roomContent
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
            if self.__roomNameMapRoomContent.get(roomName):
                self.__roomNameMapRoomContent.pop(roomName)
                saveRoomListToFile(self.getRoomList())
        return 'Delete room succeed'

    def renameRoom(self, oldRoomName, newRoomName):
        '''
            Rename the folder of the room
            Rename Key of self.__roomContentListDict
        '''
        if os.path.exists(ROOM_PATH + oldRoomName):
            if not os.path.exists(ROOM_PATH + newRoomName):
                # rename folder
                shutil.move(ROOM_PATH + oldRoomName, ROOM_PATH + newRoomName)
                roomContent = self.__roomNameMapRoomContent[oldRoomName]
                roomContent['name'] = newRoomName
                self.__roomNameMapRoomContent[newRoomName] = roomContent
                saveRoomContentToFile(roomContent)
                self.__roomNameMapRoomContent.pop(oldRoomName)
                saveRoomListToFile(self.getRoomList())


    def getRoomJsonList(self):
        ''' get room list which dumps by json'''
        roomList = self.getRoomList()
        return json.dumps(roomList)

    # ################################################################# #
    # basic functions
    def getRoomContent(self, roomName):
        ''' room content getter '''
        return self.__roomNameMapRoomContent.get(roomName)

    def getRoomContentListDict(self):
        return self.__roomNameMapRoomContent


    def getRoomList(self):
        ''' room list getter '''
        roomList = copy.deepcopy(list(self.__roomNameMapRoomContent.values()))
        # roomList don't need devices' information
        for index in range(len(roomList)):
            roomList[index]['devices'] = []
        return roomList


    def saveRoomListAndRoomContentToFile(self):
        ''' save room list and room content to file at regular time '''

        # save room list
        saveRoomListToFile(self.getRoomList())

        roomContentList = list(self.__roomNameMapRoomContent.values())
        for roomContent in roomContentList:
            saveRoomContentToFile(roomContent)
        print('Save finished.')
    # ################################################################# #
