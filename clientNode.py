import socket
class ClientNode():
	nodeId = 0
	neighbors = []
	UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
	hostname = socket.gethostname()
	localIP = socket.gethostbyname(hostname)
	localPort = 2019
	
	def __init__(self, ServerIP, PortIP):
		self.ServerIP = ServerIP
		self.PortIP = PortIP
		self.run()
	
	def run(self):
		self.sendRequest()
		self.receiveRequest()
	
	def sendRequest(self):
		clientRequest = str(self.localIP) + " " + str(self.localPort)
		bytesToSend = str.encode(clientRequest)
		serverAddress = (self.ServerIP, self.PortIP)
		#Here we should use the send secure udp
		self.UDPClientSocket.sendto(bytesToSend, serverAddress)
		print("Envié solicitud con dirección " + clientRequest)
	
	def receiveRequest(self):
		print("Recibí respuesta")
		#msgFromServer = self.UDPClientSocket.recvfrom(1024)
		
		