import socket

class secureUDP():
	
	def __init__(self, ip = "", puerto = 0): #constructor
		self.SN = 0
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.sock.settimeout(1)
		self.crearSocket(ip,puerto)

	def crearSocket(self,ip,puerto):
		server = (ip,puerto)
		self.sock.bind(server)

	def send(self, datos,ip,puerto):
		serverAddress = (ip, puerto)
		msgFinal = (self.SN).to_bytes(1, byteorder="big") + datos
		self.sock.sendto(datos, serverAddress)
		ack = False
		counter = 0
		while not ack and counter != 3:
			try:
				self.sock.recvfrom(6)
				ack = True
			except socket.timeout:
				counter = counter + 1
				self.sock.sendto(datos, serverAddress)
		return 0

		

	def receive(self):
		msg, address = self.sock.recvfrom(1024)
		ack = (1).to_bytes(1, byteorder="big")
		received = False
		while not received:
			self.sock.sendto(ack, address)
			#Si se pierde ACK
			try:
				self.sock.recvfrom(1024)
			except socket.timeout:
				received = True
		return msg