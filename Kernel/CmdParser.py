'''CmdParser.py
Parser cmd that from app
'''
import copy
import json
import datetime
from Kernel.DeviceHandler import buildNewDeviceDict

class CmdParser:
    def __init__(self, iotManager):
        self.IotManager = iotManager

    def setCommand(self, conn, target, value):
        target = target.split(':')
        if target[0] == 'room':
            pass
        elif target[0] == 'device':
            pass
        elif target[0] == 'deviceContent':
            roomName, deviceName, deviceContentName = target[1].split('/')
            deviceHandler = self.IotManager.getDeviceHandler()
            conn.sendall(deviceHandler.setValueToDeviceContent(roomName, deviceName, deviceContentName, value).encode())
        print("Finished.")
        conn.close()

    def	getCommand(self, conn, target, value):
        target = target.split(':')
        if target[0] == 'server' and value == 'checkServices':
            conn.sendall("Server is ready".encode())
        elif target[0] == 'room' and value == 'roomlist':
            roomHandler = self.IotManager.getRoomHandler()
            conn.sendall(roomHandler.getRoomJsonList().encode())
        elif target[0] == 'device' and value == 'devicelist':
            sendJson = self.buildJSON(target[1])
            conn.sendall(sendJson.encode())
        print("Finished.")
        conn.close()

    def addCommand(self, conn, target, value):
        target = target.split(':')
        if target[0] == 'room':
            roomHandler = self.IotManager.getRoomHandler()
            conn.sendall(roomHandler.addRoom(value).encode())
        elif target[0] == 'device':
            deviceUuid = value
            roomName, deviceName = target[1].split('/')
            deviceDict = buildNewDeviceDict(deviceName, deviceUuid)
            deviceHandler = self.IotManager.getDeviceHandler()
            conn.sendall(deviceHandler.addDevice(roomName, deviceDict).encode())
        print("Finished.")
        conn.close()

    def delCommand(self, conn, target, value):
        if target.split(':')[0] == 'room':
            roomHandler = self.IotManager.getRoomHandler()
            conn.sendall(roomHandler.delRoom(value).encode())
        elif target.split(':')[0] == 'device':
            roomName = target.split(':')[1]
            deviceName = value
        print("Finished.")
        conn.close()

    def commandParser(self, conn, recvdata):
        if recvdata['identity'] == 'app':
            command = recvdata
            # cmd, target, value = json.loads(Json)
            # 以免json的Key顺序乱了，不够保险
            cmd, target, value = command['cmd'], command['target'], command['value']
            if cmd == "get":
                self.getCommand(conn, target, value)
            elif cmd == 'set':
                self.setCommand(conn, target, value)
            elif cmd == 'add':
                self.addCommand(conn, target, value)
            elif cmd == 'del':
                self.delCommand(conn, target, value)
        elif recvdata['identity'] == 'device':
            self.IotManager.deviceHandler.setupIotServer(conn, recvdata)


    def buildJSON(self, roomName):
        deviceList = []
        roomContent = copy.deepcopy(self.IotManager.roomHandler.getRoomContent(roomName))
        for d in roomContent['devices']:
            if d['status'] is True:
                deviceAttribute = self.IotManager.deviceHandler.getDeviceAttributeByUuid(d['uuid'])
                # pop key: 'getter' or 'setter'
                for deviceContent in deviceAttribute['deviceContent']:
                    if deviceContent.get('getter') is not None:
                        deviceContent.pop('getter')
                    elif deviceContent.get('setter') is not None:
                        deviceContent.pop('setter')
                deviceAttribute['status'] = True
                deviceList.append(deviceAttribute)
            elif d['status'] is False:
                d['deviceContent'] = []
                deviceList.append(d)

        roomjson = {}
        roomjson['name'] = roomName
        roomjson['updateTime'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        roomjson['devices'] = deviceList

        return json.dumps(roomjson)
