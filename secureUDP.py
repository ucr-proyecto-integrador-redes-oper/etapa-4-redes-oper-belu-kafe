import socket

class secureUDP():

	def __init__(self): #constructor
		pass

	def crearSocket(ip,puerto):
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
	sUDP = secureUDP()

if __name__ == '__main__': main()
