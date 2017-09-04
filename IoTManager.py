import os
import json
import pickle
import shutil
import threading
from GlobalConstant import ROOM_PATH, RoomListFile


iotServerList = []


class IotManager:
    '''IotManager
        Manage IotServer and IotDevice
        Including access IotDevice and setup IotServer
    '''
    roomList = []

    def __init__(self):
        if os.path.exists(RoomListFile):
            with open(RoomListFile, 'rb') as roomListFileRb:
                self.roomList = pickle.load(roomListFileRb)
            for roomName in self.roomList:
                room = ROOM_PATH + roomName
                with open(room+'/.deviceListFile.pkl', 'wb') as roomContentFile:
                    roomContent = pickle.load(roomContentFile)
                    exec('self.' + roomName + ' = ' + roomContent)
                    for device in roomContent['devices']:
                        exec('self.' + roomName + '["devices"]')


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