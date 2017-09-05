'''RoomHandler
Add room
del room
get roomList
build roomDict
'''
import os
import json
import pickle
import shutil
from GlobalConstant import ROOM_PATH, RoomListFile, STANDARD_INITIAL_TIME
from IotManager import IotManager
from IotManager import getRoomListFromIotManager
from IotManager import deleteRoomInIotManager
from IotManager import addRoomtoIotManager



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
    deleteRoomInIotManager(roomName)
    return getRoomJsonList()


def getRoomJsonList():
    ''' get room list which dumps by json'''
    # get lastest room list from IotManager
    roomList = getRoomListFromIotManager()
    return json.dumps(roomList)


def getRoomListFromFile():
    ''' get room list form .roomListFile.pkl '''
    if os.path.exists(ROOM_PATH + '.roomListFile.pkl') is False:
        saveRoomListToFile([])
    with open(ROOM_PATH + '.roomListFile.pkl', 'rb') as roomListFileRb:
        roomList = pickle.load(roomListFileRb)
    return roomList


def saveRoomListToFile(roomList):
    ''' save room list to Rooms/.roomListFile.pkl '''
    with open(RoomListFile, 'wb') as roomListFileWb:
        pickle.dump(roomList, roomListFileWb)


def getRoomContentFromFile(roomName):
    ''' get room content from Rooms/<roomname>/.roomContentFile.pkl '''
    roomContentFile = ROOM_PATH + roomName + '/.roomContentFile.pkl'
    if os.path.exists(roomContentFile) is False:
        saveRoomContentToFile(buildNewRoomContentDict(roomName))
    with open(roomContentFile, 'rb') as roomContentFileRb:
        roomContent = pickle.load(roomContentFileRb)
    return roomContent

def saveRoomContentToFile(roomContent):
    ''' save room content to  Rooms/<roomname>/.roomContentFile.pkl '''
    with open(ROOM_PATH + roomContent['name'] + '/.roomContentFile.pkl', 'wb') as roomContentFileWb:
        pickle.dump(roomContent, roomContentFileWb)

def buildNewRoomContentDict(roomName):
    ''' build a room content by room content blueprint '''
    roomDict = {"name": roomName,
                "updateTime": STANDARD_INITIAL_TIME,
                "devices": []}
    return roomDict
