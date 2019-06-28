import socket
from Util import str_ip_to_tuple, ip_to_bytes, ip_tuple_to_str, ip_to_int_tuple
from struct import *
from secureUDP import secureUDP
import random
import sys # Para pasar argumentos
import re # Para usar RegEx (Expresiones Regulares)

class ClientNode():
	
	def __init__(self, myIp ,serverIP, serverPort):
		self.localIP = myIp
		self.localPort = random.randint(10000, 65000)	
		self.serverIP = serverIP
		self.serverPort = serverPort
		self.secureUDP = secureUDP(self.localIP, self.localPort)
		self.nodoId = 0
		self.vecinos = []
		hiloConsola = Thread(target=self.consola, args=())
		hiloConsola.start()
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
			msgId = int(infoNodo[0])
			self.nodoId = int.from_bytes(infoNodo[1:3], "big")
			if int(msgId) == 15:
				vecino = int.from_bytes(infoNodo[3:5],"big")
				if self.isRepeated(vecino) == False:
					self.vecinos.append((vecino, 0, 0))
			elif int(msgId) == 16:
				vecino = int.from_bytes(infoNodo[3:5],"big")
				vecinoIP = ip_tuple_to_str(ip_to_int_tuple(infoNodo[5:9]))
				vecinoPort = int.from_bytes(infoNodo[9:11],"big")
				if self.isRepeated(vecino) == False:
					self.vecinos.append((vecino, vecinoIP, vecinoPort))
				#self.helloVecino(vecinoIP, vecinoPort)
			print(self.vecinos)
	
	def isRepeated(self, nodoId):
		for n in self.vecinos:
			if n[0] == nodoId:
				return True
		return False

	def consola(self):
		while True:
			resp = input()
			if resp == "1":
				print("Yo soy " + str(self.nodoId))
				for n in self.vecinos:
					print(n)

def main():
	myIp = ""
	ip = ""
	port = 0
	if len(sys.argv) > 2:
		myHost = str(sys.argv[1])
		host = str(sys.argv[2])
		puerto = str(sys.argv[3])
		regex = r"\b(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b"
		x = re.search(regex, ip)
		try:
			if myHost == "localhost" and host == "localhost":
				ip = host
				myIp = myHost
				port = int(puerto)
			else:
				ip = host
				myIp = myHost	
				port = int(puerto)
		except:
			print("Direcciónes IP Invalidas")
			sys.exit(0)
	else:
		print("No ingresó argumentos: ")
		print("Debe ingresar ip y puerto en los argumentos")
		sys.exit(0)

	client = ClientNode(myIp, ip, port)
	
if __name__ == '__main__':
	main()
		
		
