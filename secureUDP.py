import socket

class secureUDP():
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	def __init__(self, ip = "", puerto = 0): #constructor
		self.crearSocket(ip,puerto)

	def crearSocket(self,ip,puerto):
		server = (ip,puerto)
		self.sock.bind(server)

	def send(datos,ip,puerto):
		serverAddress = (ip, puerto)
		self.sock.sendto(datos, serverAddress)

	def receive(puerto):
		msg = self.sock.recvfrom(1024)
		return msg
