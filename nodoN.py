import socket


class nodoN():

	def __init__(self, ip, puerto): #constructor
		self.ip = ip
		self.puerto = puerto

		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

		server_address = ip
		server_port = puerto

		server = (server_address,server_port)
		sock.bind(server)
		print("Listening on " + server_address + ":" + str(server_port))

		while True:
			payload, client_address = sock.recvfrom(1024)
			print(payload)

def main():
	servidor = nodoN('0.0.0.0',8888)

if __name__ == '__main__': main()
