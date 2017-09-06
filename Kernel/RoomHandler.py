'''RoomHandler
Add room
del room
get roomList
build roomDict
'''
import os
import json
import shutil
from GlobalConstant import ROOM_PATH
from IotManager import addRoomtoIotManager
from IotManager import deleteRoomInIotManager
from IotManager import getRoomListFromIotManager
from FileHandler import buildNewRoomContentDict
from FileHandler import saveRoomContentToFile
from FileHandler import saveRoomListToFile


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
