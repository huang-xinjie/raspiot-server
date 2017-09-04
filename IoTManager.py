import os
import json
import time
import pickle
import shutil
import threading
from GlobalConstant import RoomListFile
from RoomHandler import getRoomListFromFile, saveRoomListToFile, saveRoomContentToFile, getRoomContentFromFile


class IotManager:
    '''IotManager
        Manage IotServer and IotDevice
        Including access IotDevice and setup IotServer
    '''

    roomList = list()
    roomContentList = list()

    def __init__(self):
        self.roomList = getRoomListFromFile()
        for room in self.roomList:
            self.buildRoomContentVariable(room['name'])
        threading.Thread(target=self.saveRoomListAndRoomContentToFileAtRegularTime, args=None)

    def buildRoomContentVariable(self, roomName):
        ''' Get room content from folder and build variable '''
        roomContent = getRoomContentFromFile(roomName)
        self.roomContentList.append(roomContent)
        for index in range(len(roomContent['devices'])):
            roomContent['devices'][index]['status'] = False
        # use every different room name to build variable
        exec('self.' + roomName + 'RoomContent = ' + roomContent)



    def setupIotServer(self, conn, recvdata):
        ''' Setup IotServer in a new thread '''
        threading.Thread(target=self.IotServerSetter, args=(conn, recvdata))
        

    def IotServerSetter(self, conn, recvdata):
        ''' setup IotServer and add it to iotServerList '''
        ip = recvdata['ip']
        mac = recvdata['mac']
        module = recvdata['iotServer']

        try:
            if os.path.exists('IotServer/' + module + '.py') is False:
                shutil.copyfile('Repository/' + module +'.py', 'IotServer/' + module + '.py')
            exec('from IotServer import ' + module)
            exec('iotServer = ' + module + '.' + module + '("' + ip + '", "'+ mac + '")')
            exec('iotServerList.append(iotServer)')
            conn.sendall(json.dumps({'response':'Setup completed'}).encode())
            #exec('print(iotServerList[0].' + iotServerList[0].buildDeviceJSON()['deviceContent'][0]['getter'] + ')')
        except Exception:
            print('Something error')

    
    def saveRoomListAndRoomContentToFileAtRegularTime(self):
        ''' save room list and room content to file at regular time '''
        while True:
            # hold it for five minutes
            time.sleep(5 * 60)
            # save room list
            saveRoomListToFile(self.roomList)
            # remove device's status before save
            for roomContent in self.roomContentList:
                for index in range(len(roomContent['devices'])):
                    roomContent['devices'][index].pop('status')
                saveRoomContentToFile(roomContent)   
