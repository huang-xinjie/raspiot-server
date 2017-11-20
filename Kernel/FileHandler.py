'''FileHandler.py

'''
import os
import pickle
from Kernel.GlobalConstant import ROOM_PATH
from Kernel.GlobalConstant import RoomListFile
from Kernel.GlobalConstant import STANDARD_INITIAL_TIME

def getRoomListFromFile():
    ''' get room list form .roomListFile.pkl '''
    if not os.path.exists(RoomListFile):
        saveRoomListToFile([])
    with open(RoomListFile, 'rb') as roomListFileRb:
        roomList = pickle.load(roomListFileRb)
    return roomList


def saveRoomListToFile(roomList):
    ''' save room list to Rooms/.roomListFile.pkl '''
    with open(RoomListFile, 'wb') as roomListFileWb:
        pickle.dump(roomList, roomListFileWb)


def getRoomContentFromFile(roomName):
    ''' get room content from Rooms/<roomname>/.roomContentFile.pkl '''
    roomContentFile = ROOM_PATH + roomName + '/.roomContentFile.pkl'
    if not os.path.exists(roomContentFile):
        saveRoomContentToFile(buildNewRoomContentDict(roomName))
    with open(roomContentFile, 'rb') as roomContentFileRb:
        roomContent = pickle.load(roomContentFileRb)
    return roomContent

def saveRoomContentToFile(roomContent):
    ''' save room content to  Rooms/<roomname>/.roomContentFile.pkl '''
    roomContentFile = ROOM_PATH + roomContent['name'] + '/.roomContentFile.pkl'
    if not os.path.exists(ROOM_PATH + roomContent['name']):
        os.makedirs(ROOM_PATH + roomContent['name'])
    with open(roomContentFile, 'wb') as roomContentFileWb:
        pickle.dump(roomContent, roomContentFileWb)


def buildNewRoomContentDict(roomName):
    ''' build a room content by room content blueprint '''
    roomContentDict = {"name": roomName,
                       "updateTime": STANDARD_INITIAL_TIME,
                       "devices": []}
    return roomContentDict
