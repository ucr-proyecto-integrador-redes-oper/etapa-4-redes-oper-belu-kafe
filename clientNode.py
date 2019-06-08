import socket
from Util import str_ip_to_tuple, ip_to_bytes, ip_tuple_to_str, ip_to_int_tuple
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
		msgIP = ip_to_bytes(str_ip_to_tuple(self.localIP))
		msgPort = (self.localPort).to_bytes(2, byteorder="big")
		msgFinal = (msgIP + msgPort)
		print(msgFinal)
		self.secureUDP.send(msgFinal, self.serverIP, self.portIP)
		#Debugging splitting(should be on Orange Node)
		print(str(msgFinal[0:4]))
		ip = ip_tuple_to_str(ip_to_int_tuple(msgFinal[0:4]))
		print(ip)
		print(str(msgFinal[5:6]))
		port = int.from_bytes(msgFinal[4:6], byteorder='big')
		print(port)

	def receiveRequest(self):
		pass
		#print("Recibí respuesta")
		#msgFromServer = self.UDPClientSocket.recvfrom(1024)
		
		
