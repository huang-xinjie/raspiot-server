import socket  
from CmdParser import *

BUFFSIZE=1024

s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)   
s.bind(("0.0.0.0",2222))  
s.listen(5)


while True:
	conn, addr = s.accept()
	print("connected by ", addr)
	recvJson = conn.recv(BUFFSIZE).decode()
	print(recvJson)
	commandParser(conn, recvJson)
s.close()  