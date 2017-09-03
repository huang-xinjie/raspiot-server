import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("192.168.1.138", 8085))
s.sendall('Reset'.encode())
s.close()