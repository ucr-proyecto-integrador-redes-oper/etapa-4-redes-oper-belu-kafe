import socket
from Util import str_ip_to_tuple, ip_to_bytes, ip_tuple_to_str, ip_to_int_tuple
from struct import *
from secureUDP import secureUDP
import random
class ClientNode():
	nodeId = 0
	neighbors = []
	localPort = random.randint(1000, 10000)
	
	def __init__(self, serverIP, serverPort):
		self.hostname = socket.gethostname()
		self.localIP = socket.gethostbyname(self.hostname)
		self.serverIP = serverIP
		self.serverPort = serverPort
		self.secureUDP = secureUDP(self.localIP, self.localPort)
		self.run()
	
	def run(self):
		self.sendRequest()
		self.receiveRequest()
	
	def sendRequest(self):
		msgIP = ip_to_bytes(str_ip_to_tuple(self.localIP))
		msgPort = (self.localPort).to_bytes(2, byteorder="big")
		msgFinal = (msgIP + msgPort)
		print("Sending request...")
		self.secureUDP.send(msgFinal, self.serverIP, self.serverPort)
		#Debugging splitting(should be on Orange Node)

	def receiveRequest(self):
		infoNodo = self.secureUDP.getMessage()
		print("Request ready: " + str(infoNodo))
		#print("Recibí respuesta")
		#msgFromServer = self.UDPClientSocket.recvfrom(1024)
		
		
