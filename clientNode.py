import socket
from secureUDP import secureUDP
class ClientNode():
	nodeId = 0
	neighbors = []
	hostname = socket.gethostname()
	localIP = socket.gethostbyname(hostname)
	
	localPort = 2019
	
	def __init__(self, serverIP, portIP):
		self.serverIP = serverIP
		self.portIP = portIP
		self.secureUDP = secureUDP(self.serverIP, self.portIP)
		self.run()
	
	def run(self):
		self.sendRequest()
		self.receiveRequest()
	
	def sendRequest(self):
		msgIP = bytearray(4)
		msgPort = (self.localPort).to_bytes(2, byteorder="big")
		IP = str(self.localIP).split('.')
		for i in range(len(IP)):
			msgIP[i] = int(IP[i])
		msgFinal = bytearray(6)
		msgFinal = (msgIP + msgPort)
		print(msgFinal)
		self.secureUDP.send(msgFinal, self.serverIP, self.portIP)
		
	
	def receiveRequest(self):
		print("Recibí respuesta")
		#msgFromServer = self.UDPClientSocket.recvfrom(1024)
		
		
