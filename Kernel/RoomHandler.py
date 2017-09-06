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
from Kernel.IotManager import addRoomtoIotManager
from Kernel.IotManager import deleteRoomInIotManager
from Kernel.IotManager import getRoomListFromIotManager
from Kernel.FileHandler import buildNewRoomContentDict
from Kernel.FileHandler import saveRoomContentToFile
from Kernel.FileHandler import saveRoomListToFile


def addRoom(roomName):
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
    roomList = addRoomtoIotManager(buildNewRoomContentDict(roomName))
    saveRoomListToFile(roomList)

    return getRoomJsonList()


def deleteRoom(roomName):
    '''
    Delete a room from roomList,
    and delete the folder of the room
    '''
    if os.path.exists(ROOM_PATH + roomName) is False:
        #return 'Room not exists.'
        return getRoomJsonList()
    # delete the folder of the room
    shutil.rmtree(ROOM_PATH + roomName)
    roomList = deleteRoomInIotManager(roomName)

    return getRoomJsonList()


def getRoomJsonList():
    ''' get room list which dumps by json'''
    # get lastest room list from IotManager
    roomList = getRoomListFromIotManager()
    return json.dumps(roomList)
