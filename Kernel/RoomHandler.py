'''RoomHandler
Add room
del room
get roomList
build roomDict
'''
import os
import json
import shutil
from Kernel.GlobalConstant import ROOM_PATH
from Kernel.FileHandler import saveRoomListToFile
from Kernel.FileHandler import saveRoomContentToFile
from Kernel.FileHandler import buildNewRoomContentDict



class RoomHandler:
    def __init__(self, iotManager):
        self.IotManager = iotManager

    def addRoom(self, roomName):
        '''
        Add new room to roomList,
        and create a new folder for the room,
        and create a .roomContentFile to record all devices of the room
        '''

        if os.path.exists(ROOM_PATH + roomName):
            return 'Room already exists.'
        # Add new folder and initial
        os.makedirs(ROOM_PATH + roomName)
        saveRoomContentToFile(buildNewRoomContentDict(roomName))
        # Add new room information to IotManager.roomList
        roomContent = buildNewRoomContentDict(roomName)
        self.IotManager.roomList.append(roomContent)
        saveRoomListToFile(self.IotManager.roomList)

        return self.getRoomJsonList()


    def deleteRoom(self, roomName):
        '''
        Delete a room from roomList,
        and delete the folder of the room
        '''
        if os.path.exists(ROOM_PATH + roomName):
            # delete the folder of the room
            shutil.rmtree(ROOM_PATH + roomName)
            ''' delete room in IotManager.roomList '''
            roomList = self.IotManager.getRoomList()
            for index in range(len(roomList)):
                if roomList[index]['name'] == roomName:
                    del roomList[index]
                    break
        else:
            #return 'Room not exists.'
            pass
        return self.getRoomJsonList()


    def getRoomJsonList(self):
        ''' get room list which dumps by json'''
        # get lastest room list from IotManager
        roomList = self.IotManager.getRoomList()
        return json.dumps(roomList)
