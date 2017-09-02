import sys
import socket

class DHT11:
    temperature = ''
    humidity = ''

    def __init__(self, deviceIp):
        self.ip = deviceIp

    def getTemperaturen(self):
        self.connectWithDevice('getTemp')
    
    def getHumidity(self):
        self.connectWithDevice('getHumidity')

    def connectWithDevice(self, cmd):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.ip, 8085))
        s.sendall(cmd.encode())
        recvdata = s.recv(1024).decode()
        s.close()
        return recvdata
