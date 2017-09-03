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
ROOM_PATH = 'Rooms/'
STANDARD_INITIAL_TIME = "2015-12-17 22:22:00"



def addRoom(newRoomName):
    '''
    Add new room to roomList,
    and create a new folder for the room,
    and create a .deviveListFile to record all devices of the room
    '''
    roomName = ROOM_PATH+newRoomName

    if os.path.exists(roomName):
        return 'Room already exists.'
    # Add new folder and initial
    os.makedirs(roomName)
    with open(roomName + '/.deviceListFile.pkl', 'wb') as deviceListFile:
        pickle.dump(buildRoomDict(newRoomName), deviceListFile)

    # Add new room information to .roomListFile
    RoomListFile = ROOM_PATH + '.roomListFile.pkl'
    if os.path.exists(RoomListFile):
        with open(RoomListFile, 'rb') as roomListFileRb:
            roomList = pickle.load(roomListFileRb)
        roomList.append(newRoomName)
        with open(RoomListFile, 'wb') as roomListFileWb:
            pickle.dump(roomList, roomListFileWb)
    else:
        with open(RoomListFile, 'wb') as roomListFileWb:
            roomList = [newRoomName]
            pickle.dump(roomList, roomListFileWb)

    return getRoomList()


def deleteRoom(roomName):
    '''
    Delete a room from roomList,
    and delete the folder of the room
    '''
    if os.path.exists(ROOM_PATH + roomName) is False:
        return 'Room not exists.'
    shutil.rmtree(ROOM_PATH + roomName)
    RoomListFile = ROOM_PATH + '.roomListFile.pkl'
    try:
        if os.path.exists(RoomListFile):
            with open(RoomListFile, 'rb') as roomListFileRb:
                roomList = pickle.load(roomListFileRb)
            roomList.remove(roomName)
            with open(RoomListFile, 'wb') as roomListFileWb:
                pickle.dump(roomList, roomListFileWb)
        else:
            with open(RoomListFile, 'wb') as roomListFileWb:
                roomList = []
                pickle.dump(roomList, roomListFileWb)
    except Exception:
        pass
    return getRoomList()


def getRoomList():
    ''' get room list form .roomListFile.pkl'''
    roomJsonList = []

    if os.path.exists(ROOM_PATH + '.roomListFile.pkl'):
        with open(ROOM_PATH + '.roomListFile.pkl', 'rb') as roomListFileRb:
            roomList = pickle.load(roomListFileRb)
            for room in roomList:
                roomJsonList.append(buildRoomDict(room))
    else:
        with open(ROOM_PATH + '.roomListFile.pkl', 'wb') as roomListFileWb:
            pickle.dump(roomJsonList, roomListFileWb)
    return json.dumps(roomJsonList)


def buildRoomDict(roomName):
    '''buildRoomDict for roomlist'''
    roomDict = {"name": roomName,
                "updateTime": STANDARD_INITIAL_TIME,
                "devices": []}
    return roomDict
