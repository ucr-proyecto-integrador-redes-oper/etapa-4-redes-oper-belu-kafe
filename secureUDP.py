import socket

class secureUDP():
	
	def __init__(self, ip = "", puerto = 0): #constructor
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.crearSocket(ip,puerto)

	def crearSocket(self,ip,puerto):
		server = (ip,puerto)
		self.sock.bind(server)

	def send(self, datos,ip,puerto):
		serverAddress = (ip, puerto)
		self.sock.sendto(datos, serverAddress)

	def receive(self):
		msg = self.sock.recvfrom(1024)
		return msg
