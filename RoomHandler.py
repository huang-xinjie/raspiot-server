import os
import json
import pickle
import shutil
ROOM_PATH = 'Rooms/'
STANDARD_INITIAL_TIME = "2015-12-17 22:22:00"

class RoomHandler:

	##
	# Add new room to roomList, 
	# and create a new folder for the room,
	# and create a .deviveListFile to record all devices of the room
	##
	def addRoom(self, newRoomName):
		roomName = ROOM_PATH+newRoomName

		if os.path.exists(roomName):
			return 'Room already exists.'
		# Add new folder and initial
		os.makedirs(roomName)
		with open(roomName + '/.deviceListFile.pkl', 'wb') as deviceListFile:
			pickle.dump(self.buildRoomDict(newRoomName), deviceListFile)
	
		#Add new room information to .roomListFile
		RoomListFile = ROOM_PATH + '.roomListFile.pkl'
		if os.path.exists(RoomListFile):
			with open(RoomListFile, 'rb') as roomListFileRb:
				roomList = pickle.load(roomListFileRb)
			roomList.append(self.buildRoomDict(newRoomName))
			with open(RoomListFile, 'wb') as roomListFileWb:
				pickle.dump(roomList, roomListFileWb)
		else:
			with open(RoomListFile, 'wb') as roomListFileWb:
				roomList = [self.buildRoomDict(newRoomName)]
				pickle.dump(roomList, roomListFileWb)
		
		return self.getRoomList()

	##
	# Delete a room from roomList,
	# and delete the folder of the room
	##
	def deleteRoom(self, roomName):
		if os.path.exists(ROOM_PATH + roomName) == False:
			return 'Room not exists.'
		shutil.rmtree(ROOM_PATH + roomName)
		RoomListFile = ROOM_PATH + '.roomListFile.pkl'
		try:
			if os.path.exists(RoomListFile):
				with open(RoomListFile, 'rb') as roomListFileRb:
					roomList = pickle.load(roomListFileRb)
				roomList.remove(self.buildRoomDict(roomName))
				with open(RoomListFile, 'wb') as roomListFileWb:
					pickle.dump(roomList, roomListFileWb)
			else:
				with open(RoomListFile, 'wb') as roomListFileWb:
					roomList = []
					pickle.dump(roomList, roomListFileWb)
		except Exception:
			pass
		return self.getRoomList()


	def getRoomList(self):
		roomJsonList = []
		
		if os.path.exists(ROOM_PATH + '.roomListFile.pkl'):
			with open(ROOM_PATH + '.roomListFile.pkl', 'rb') as roomListFileRb:
				roomList = pickle.load(roomListFileRb)
				for room in roomList:
					roomJsonList.append(room)
		else:
			with open(ROOM_PATH + '.roomListFile.pkl', 'wb') as roomListFileWb:
				pickle.dump(roomJsonList, roomListFileWb)
		return json.dumps(roomJsonList)


	def buildRoomDict(self, roomName):
		roomDict = {"name":roomName,
				"updateTime":STANDARD_INITIAL_TIME,
				"devices":[]}
		return roomDict