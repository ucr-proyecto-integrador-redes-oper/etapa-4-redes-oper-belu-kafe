import socket

class secureUDP():
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	def __init__(self): #constructor
		pass

	def crearSocket(self,ip,puerto):
		server = (ip,puerto)
		self.sock.bind(server)
		print("Listening on " + ip + ":" + str(puerto))

		while True:
			payload, client_address = self.sock.recvfrom(1024)
			print(payload)

	def send(datos,ip,puerto):
		serverAddress = (ip, puerto)
		self.sock.sendto(datos, serverAddress)

	def receive(puerto):
		pass
