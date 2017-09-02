import json
import datetime
from RoomHandler import *
roomHandler = RoomHandler()

def setCommand(conn, target, value):
	pass
	

def	getCommand(conn, target, value):
	if target == 'server' and value == 'checkServices':
		conn.sendall("Server is ready".encode())
	elif target == 'room' and value == 'roomlist':
		conn.sendall(roomHandler.getRoomList().encode())
	elif target.split(':')[0] == 'device' and value == 'devicelist':
		sendJson = buildJSON(target.split(':')[1])
		conn.sendall(sendJson.encode())
	print("Finished.")
	conn.close()
	
def addCommand(conn, target, value):
	if target.split(':')[0] == 'room':
		conn.sendall( roomHandler.addRoom(value).encode())
	elif target.split(':')[0] == 'device':
		pass
	conn.close()

def delCommand(conn, target, value):
	if target.split(':')[0] == 'room':
		conn.sendall(roomHandler.deleteRoom(value).encode())
	elif target.split(':')[0] == 'device':
		roomName = target.split(':')[1]
		deviceName = value
	conn.close()


def commandParser(conn, Json):
	# cmd, target, value = json.loads(Json) #以免json的Key顺序乱了，不够保险
	command = json.loads(Json)
	cmd, target, value = command['cmd'], command['target'], command['value']
	if cmd == "get":
		getCommand(conn, target, value)
	elif cmd == 'set':
		setCommand(conn, target, value)
	elif cmd == 'add':
		addCommand(conn, target, value)
	elif cmd == 'del':
		delCommand(conn, target, value)
	


def buildJSON(roomName):
	deviceList = []
	
	deviceContentList1 = [{ "type":"switch", "name":"开关", "value":"false" }]
	uuid1 = "28:E1:4C:BC:70:0B"
	deviceName1 = "风扇"
	device1 = {}
	device1['name'] = deviceName1
	device1['uuid'] = uuid1
	device1['deviceContent'] = deviceContentList1
	deviceList.append(device1)
	
	deviceContentList2 = [{ "type":"text", "name":"Temperature", "value":"32.5*C" }, { "type":"text", "name":"Humidity", "value":"60%" }, { "type":"image", "name":"image", "value":"http://www.raspiot.cn/static/images/raspIot.jpg" }]
	uuid2 = "28:E1:4C:BC:70:0C"
	deviceName2 = "DHT11"
	device2 = {}
	device2['name'] = deviceName2
	device2['uuid'] = uuid2
	device2['deviceContent'] = deviceContentList2
	deviceList.append(device2)
	
	deviceContentList3 = [{ "type":"text", "name":"Temperature", "value":"32.5*C" }, { "type":"text", "name":"Humidity", "value":"65%" }]
	uuid3 = "28:E1:4C:BC:70:0D"
	deviceName3 = "DHT12"
	device3 = {}
	device3['name'] = deviceName3
	device3['uuid'] = uuid3
	device3['deviceContent'] = deviceContentList3
	deviceList.append(device3)
	
	
	
	roomjson = {}
	roomjson['name'] = roomName
	roomjson['updateTime'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	roomjson['devices'] = deviceList
	

	return json.dumps(roomjson)