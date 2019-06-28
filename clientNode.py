import socket
from Util import str_ip_to_tuple, ip_to_bytes, ip_tuple_to_str, ip_to_int_tuple
from struct import *
from secureUDP import secureUDP
import random
import sys # Para pasar argumentos
import re # Para usar RegEx (Expresiones Regulares)

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
		self.vecinos = []
		self.run()
	
	def run(self):
		self.sendRequest()
		self.receiveRequest()
	
	def sendRequest(self):
		msgId = (14).to_bytes(1, byteorder="big")	
		msgIP = ip_to_bytes(str_ip_to_tuple(self.localIP))
		msgPort = (self.localPort).to_bytes(2, byteorder="big")
		msgFinal = (msgId + msgIP + msgPort)
		print("Sending request...")
		self.secureUDP.send(msgFinal, self.serverIP, self.serverPort)
		#Debugging splitting(should be on Orange Node)

	def receiveRequest(self):
		while True:
			infoNodo = self.secureUDP.getMessage()
			print("Request ready: " + str(infoNodo))

def main():
	host = ""
	port = 0
	if len(sys.argv) > 2:
		ip = str(sys.argv[1])
		puerto = str(sys.argv[2])
		regex = r"\b(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b"
		x = re.search(regex, ip)
		try:
			if ip=="localhost":
			   host=ip
			   port=int(puerto)
			else:
			   host=ip
			   port=int(puerto)
		except:
			print("Dirección IP Invalida")
			sys.exit(0)
	else:
		print("No ingresó argumentos: ")
		print("Debe ingresar ip y puerto en los argumentos")
		sys.exit(0)
	client = ClientNode(host, port)
	
if __name__ == '__main__':
	main()
		
		
