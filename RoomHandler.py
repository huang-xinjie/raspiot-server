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
    # Add new room information to .roomListFile
    roomList = getRoomListFromFile()
    roomList.append(buildNewRoomContentDict(roomName))
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
    shutil.rmtree(ROOM_PATH + roomName)
    try:
        roomList = getRoomListFromFile()
        for index in len(roomList):
            if roomList[index]['name'] == roomName:
                del roomList[index]
                break
        saveRoomListToFile(roomList)
    except Exception:
        print('delete room error')
    return getRoomJsonList()


def getRoomJsonList():
    roomList = getRoomListFromFile()
    return json.dumps(roomList)


def getRoomListFromFile():
    ''' get room list form .roomListFile.pkl'''
    if os.path.exists(ROOM_PATH + '.roomListFile.pkl') is False:
        saveRoomListToFile([])
    with open(ROOM_PATH + '.roomListFile.pkl', 'rb') as roomListFileRb:
        roomList = pickle.load(roomListFileRb)
    return roomList


def saveRoomListToFile(roomList):
    with open(RoomListFile, 'wb') as roomListFileWb:
        pickle.dump(roomList, roomListFileWb)


def getRoomContentFromFile(roomName):
    roomContentFile = ROOM_PATH + roomName + '/.roomContentFile.pkl'
    if os.path.exists(roomContentFile) is False:
        saveRoomContentToFile(buildNewRoomContentDict(roomName))
    with open(roomContentFile, 'rb') as roomContentFileRb:
        roomContent = pickle.load(roomContentFileRb)

    return roomContent

def saveRoomContentToFile(roomContent):
    with open(ROOM_PATH + roomContent['name'] + '/.roomContentFile.pkl', 'wb') as roomContentFileWb:
        pickle.dump(roomContent, roomContentFileWb)

def buildNewRoomContentDict(roomName):
    '''build a room content by using blueprint'''
    roomDict = {"name": roomName,
                "updateTime": STANDARD_INITIAL_TIME,
                "devices": []}
    return roomDict
