
import os
import pickle
from GlobalConstant import ROOM_PATH
from GlobalConstant import RoomListFile
from GlobalConstant import STANDARD_INITIAL_TIME

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
