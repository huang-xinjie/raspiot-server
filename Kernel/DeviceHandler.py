'''DeviceHandler
   Add device
   del device
   move device
   rename device
'''
import os
import json
import time
import shutil
import platform
import importlib
import threading
import subprocess
from Kernel.FileHandler import saveRoomContentToFile
from Kernel.GlobalConstant import MY_DEVICES
from Kernel.GlobalConstant import ROOM_PATH


class DeviceHandler(object):
    '''
    DeviceHandler is responsible for add a new device to access in raspIot,
    and get a json contains device attribute for onLineIotServerListDict by device's uuid,
    and set device content to a new value, means control iot devices.
    and check those online devices is still aliving or not in a child thread,
    and setup iotServer in a child thread when a iot device access in.

    Attributes:
        All is private
    '''
    __deviceUuidMapIotServer = dict()
    __devicesUuidMapRoom = dict()
    PingCmd = None              # for check device alive

    def __init__(self, iotManager):
        ''' DeviceHandler initial
        Args:
            iotManager: this object is one attribute of the iotManager

        Returns:
            None
        '''
        self.IotManager = iotManager
        roomContentList = list(self.IotManager.roomHandler.getRoomContentListDict().values())
        for roomContent in roomContentList:
            for index in range(len(roomContent['devices'])):
                # using uuid to map room, make room search faster
                deviceUuid = roomContent['devices'][index]['uuid']
                self.__devicesUuidMapRoom[deviceUuid] = roomContent['name']
        threading.Thread(target=self.checkIsIotDeviceAliving, args=()).start()


    def addDevice(self, roomName, device):
        ''' addDevice method
        Args:
            roonName: the name of the room which new device belong to.
            device: a dict instance that include all informations of the new device.

        Returns:
            A str contains the result of add device succeed or not.
            'Device already exists.' or 'Add device succeed.'
        '''
        deviceUuid = device['uuid'].upper()
        checkRoomName = self.__devicesUuidMapRoom.get(deviceUuid)
        if checkRoomName and checkRoomName != MY_DEVICES:
            return 'Device already exists.'
        self.__devicesUuidMapRoom[deviceUuid] = roomName
        room = self.IotManager.roomHandler.getRoomContent(roomName)
        room['devices'].append(device)
        saveRoomContentToFile(room)
        return 'Add device succeed.'

    def renameDevice(self, deviceUuid, newDeviceName):
        '''renameDevice method
        Args:
            deviceUuid
            newDeviceName
        '''
        iotServer = self.__deviceUuidMapIotServer.get(deviceUuid)
        if iotServer:
            iotServer.name = newDeviceName
        roomName = self.__devicesUuidMapRoom.get(deviceUuid)
        if roomName:
            roomHandler = self.IotManager.getRoomHandler()
            roomContent = roomHandler.getRoomContent(roomName)
            for index in range(len(roomContent['devices'])):
                if roomContent['devices'][index]['uuid'] == deviceUuid:
                    roomContent['devices'][index]['name'] = newDeviceName
                    saveRoomContentToFile(roomContent)
                    break

    def moveDevice(self, deviceUuid, newRoomName):
        ''' moveDevice method
        Args:
            deviceUuid: uuid of the device which need to move
            newRoomName: the new room that device will move to
        '''
        roomName = self.__devicesUuidMapRoom.get(deviceUuid)
        if roomName:
            roomContent = self.IotManager.roomHandler.getRoomContent(roomName)
            for index in range(len(roomContent['devices'])):
                print(roomContent['devices'][index])
                if deviceUuid == roomContent['devices'][index]['uuid']:
                    device = roomContent['devices'][index]
                    self.__devicesUuidMapRoom.pop(deviceUuid)
                    if self.addDevice(newRoomName, device) == 'Add device succeed.':
                        roomContent['devices'].remove(device)
                        saveRoomContentToFile(roomContent)
                    else:
                        self.__devicesUuidMapRoom[deviceUuid] = roomName
                    break

    def moveAllDevice(self, oldRoomName, newRoomName):
        '''moveAllDevice method
        Args:
            oldRoomName: roomName of devices those need to move
            newRoomNAME: the new room that devices will move to
        '''
        roomContent = self.IotManager.roomHandler.getRoomContent(oldRoomName)
        if roomContent:
            for d in roomContent['devices']:
                self.moveDevice(d['uuid'], newRoomName)

    def delDevice(self, deviceUuid):
        ''' delDevice method
        Args:
            deviceUuid: uuid of the device which will be delete
        '''
        roomName = self.__devicesUuidMapRoom.get(deviceUuid)
        if roomName:
            roomContent = self.IotManager.roomHandler.getRoomContent(roomName)
            for index in range(len(roomContent['devices'])):
                print(roomContent['devices'][index])
                if deviceUuid == roomContent['devices'][index]['uuid']:
                    device = roomContent['devices'][index]
                    self.__devicesUuidMapRoom.pop(deviceUuid)
                    roomContent['devices'].remove(device)
                    saveRoomContentToFile(roomContent)
                    break

    def getDeviceAttributeByUuid(self, uuid):
        '''getDeviceJsonByUuid method
        Args:
            uuid: uuid of the device which you want to get it's device attribute

        Returns:
            a dict of device's attribute
        '''
        if self.__deviceUuidMapIotServer.get(uuid) is None:
            return None
        iotServer = self.__deviceUuidMapIotServer.get(uuid)
        try:
            attribute = iotServer.getDeviceAttribute()
        except Exception:
            attribute = None
        return attribute

    def setValueToDeviceContent(self, roomName, deviceName, deviceContentName, value):
        '''setValueToDeviceContent method
        Args:
            roomName: a str representing the name of the room that the device belong to
            deviceName: a str representing the name of the device content that want to send new value
            deviceContentName: a str representing the name that need to set new value
            value: a str of new value

        Returns:
            a str representing the value of the device content after set new value

        Raises:
            AttributeError: an error occurred accessing the iotServer.getDeviceAttribute() method.
            KeyError: an error occurred accessing deviceContent's 'setter' Key.
        '''
        try:
            room = self.IotManager.roomHandler.getRoomContent(roomName)
            for index in range(len(room['devices'])):
                if room['devices'][index]['name'] == deviceName:
                    deviceUuid = room['devices'][index]['uuid']
                    break

            iotServer = self.__deviceUuidMapIotServer[deviceUuid]
            device = iotServer.getDeviceAttribute()
            for index in range(len(device['deviceContent'])):
                if device['deviceContent'][index]['name'] == deviceContentName:
                    deviceContentSetter = device['deviceContent'][index]['setter']
                    break

            exec('iotServer.' + deviceContentSetter + '("' + value + '")')
        except Exception as reason:
            print(__file__ + " Error: " + str(reason))
            return "false"
        return "true"


    def checkIsIotDeviceAliving(self):
        ''' checkIsIotDeviceAliving method
        At regularly time, ping all the iot device to check iot devices is Aliving or not
        and it should work in a child thread, because it will always work.

        Args:
            None

        Raisers:
            TypeError: an error occurred accessing ping result in not utf-8 encoding
        '''
        systype = platform.system()
        if systype == 'Windows':
            DeviceHandler.PingCmd = 'ping -n 3 '
        elif systype == 'Linux':
            DeviceHandler.PingCmd = 'ping -c 3 '
        while True:
            time.sleep(10)  # 10 seconds
            for iotServer in list(self.__deviceUuidMapIotServer.values()):
                try:
                    deviceIp = iotServer.ip
                    deviceUuid = iotServer.uuid
                    if self.pingDevice(deviceIp) is False:
                        del iotServer       # device unreachable, shut iotServer down
                        self.__deviceUuidMapIotServer.pop(deviceUuid)    # iotServer offline
                        roomName = self.__devicesUuidMapRoom[deviceUuid]
                        roomContent = self.IotManager.roomHandler.getRoomContent(roomName)
                        for index in range(len(roomContent['devices'])):
                            if roomContent['devices'][index]['uuid'] == deviceUuid:
                                # set iotServer status to offline
                                roomContent['devices'][index]['status'] = False
                                print(roomName + ': ' + roomContent['devices'][index]['name'] + ' offline')
                                break
                        saveRoomContentToFile(roomContent)
                except Exception as reason:
                    print(str(reason))
                    # End threading
                    return

    def pingDevice(self, deviceIp):
        if deviceIp is None:
            return False
        pingCmd = DeviceHandler.PingCmd + deviceIp
        try:
            pingResult = subprocess.check_output(pingCmd, shell=True).decode()
            return True
        # device unreachable
        except subprocess.CalledProcessError:
            return False


    def setupIotServer(self, conn, recvdata):
        ''' setupIotServer method
        Setup IotServer in a new thread when iot device access in.
        '''
        threading.Thread(target=self.IotServerSetter, args=(conn, recvdata)).start()


    def IotServerSetter(self, conn, recvdata):
        ''' IotServerSetter method
        Parser recvdata that from iot device to get ip, uuid, iotServer module, repository, etc.
        Get iotServer module from repository, and set it up, and add it to onlineIotServerListDict.

        Args:
            conn: a connect from iot device
            recvdata: a dict contains device's information. For example:{"uuid":"5c:cf:7f:14:73:ab",
                                                                         "repository":"raspIot",
                                                                         "device":"ds18b20",
                                                                         "iotServer":"DS18B20",
                                                                         "identity":"device",
                                                                         "ip":"192.168.17.138"}
        Returns:
            None. But it will reply the result of setup iotServer to the device by conn.

        Raises:
            KeyError: an error occurred accessing recvdata's Key.
        '''
        ip = recvdata['ip']
        uuid = recvdata['uuid'].upper()
        moduleName = className = recvdata['iotServer']

        if not self.__devicesUuidMapRoom.get(uuid):
            # No UNAUTHORIZED_ACCESS_MODE: reject
            conn.sendall(json.dumps({'response':'Setup completed'}).encode()) # for the moment
            print('Unauthorized devices: ' + uuid + ' is rejected to access in.')
            conn.close()
            # save information of the unauthorized device
            deviceName = recvdata['device'] + '_' + uuid.replace(':', '')[-4:]
            deviceInfo = buildNewDeviceDict(deviceName, uuid)
            msg = "An unauthorized device try to access in.\nThis is its information: " + str(deviceInfo)
            print(msg)
            print("Finished.")
            return
        else:
            # search which room it's belong to
            roomName = self.__devicesUuidMapRoom[uuid]
            deviceName = self.getDeviceNameByUuid(uuid)
        try:
            # get iotServer module from device's Repository
            IotServerFile = moduleName + '.py'
            IotServerPath = ROOM_PATH + roomName + '/' + IotServerFile
            if not os.path.exists(IotServerPath):
                shutil.copyfile('Repository/' + IotServerFile, IotServerPath)
            # import module from IotServer/
            iotServerModule = importlib.import_module('Rooms.' + roomName + '.' + moduleName)
            # import class from module
            iotServerClass = getattr(iotServerModule, className)

            # instantiation
            iotServer = iotServerClass(ip, uuid, deviceName)
            if not self.__deviceUuidMapIotServer.get(uuid):
                self.__deviceUuidMapIotServer[uuid] = iotServer

            if roomName == MY_DEVICES:
                deviceDict = buildNewDeviceDict(deviceName, uuid)
                deviceDict['status'] = True

            # set status of this iotServer True
            devices = self.IotManager.roomHandler.getRoomContent(roomName)['devices']

            for index in range(len(devices)):
                if devices[index]['uuid'] == uuid:
                    devices[index]['status'] = True
                    print(roomName + ': ' + devices[index]['name'] + ' online')
                    break
            conn.sendall(json.dumps({'response':'Setup completed'}).encode())
            print("Finished.")
            conn.close()
        except Exception as reason:
            print(__name__ +' Error: ' + str(reason))

    def getDeviceUuidByName(self, roomName, deviceName):
        roomHandler = self.IotManager.getRoomHandler()
        roomContent = roomHandler.getRoomContent(roomName)
        if roomContent:
            for d in roomContent['devices']:
                if d['name'] == deviceName:
                    return d['uuid']

    def getDeviceNameByUuid(self, uuid):
        roomName = self.__devicesUuidMapRoom[uuid]
        room = self.IotManager.roomHandler.getRoomContent(roomName)
        try:
            devices = room['devices']
            for index in range(len(devices)):
                if devices[index]['uuid'] == uuid:
                    deviceName = devices[index]['name']
                    return deviceName
        except Exception:
            return None

    def getDeviceIpByUuid(self, uuid):
        iotServer = self.__deviceUuidMapIotServer.get(uuid)
        if iotServer is not None:
            return iotServer.ip
        else:
            return None


def buildNewDeviceDict(deviceName, deviceUuid):
    ''' buildNewDeviceDict function
    Build a device by a blueprint of device attribute

    Args:
        deviceName: a str representing name of the device.
        deviceUuid: a str representing uuid of the device.

    Returns:
        deviceDict: a dict of device attribute
    '''
    deviceDict = {"name": deviceName,
                  "uuid": deviceUuid,
                  "status": False}
    return deviceDict
