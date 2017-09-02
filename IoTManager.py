import time
import json
import socket

BUFFSIZE = 1024

s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)   
s.bind(("0.0.0.0",23333))  
s.listen(5)

iotServerList = []

def IotHandler(recvdata):
	time.sleep(3)
	ip = recvdata['ip']
	module = recvdata['iotServer']
	try:
		exec('from IoTServer import ' + module)
		exec('iotServer = ' + module + '.' + module + "('" + ip + "')")
		exec('iotServerList.append(iotServer)')
		exec('print(iotServerList[0].' + iotServerList[0].buildDeviceJSON()['deviceContent'][0]['getter'] + ')')
	except Exception:
		return 'Something error'

while True:
	conn, addr = s.accept()
	print("connected by ", addr)
	recvjson = conn.recv(BUFFSIZE).decode()
	recvdata = json.loads(recvjson)
	print(recvdata)
	conn.sendall(json.dumps({ 'response':'finish'}).encode())
	IotHandler(recvdata)
s.close()