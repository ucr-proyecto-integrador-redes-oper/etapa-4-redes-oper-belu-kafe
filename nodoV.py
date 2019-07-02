from secureUDP import secureUDP
from Util import str_ip_to_tuple, ip_to_bytes, ip_tuple_to_str, ip_to_int_tuple
import sys
import socket
import csv
from threading import Lock, Thread
from time import sleep
import re # Para usar RegEx (Expresiones Regulares)

class nodoV():
	
	# constructor de la clase nodo
	def __init__(self, myIp ,ip, port):  # constructor
		self.BLUE_PORT = 19999
		self.hostname = socket.gethostname()
		self.localIP = myIp
		self.socketNV = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.socketNV.bind((self.localIP, self.ORANGE_PORT))

		self.secureUDPBlue = secureUDP(self.localIP, self.BLUE_PORT)
		


	

	
		

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

	print("Mi Ip es " + myIp)
	print("El siguiente IP es " + ip)
	print("El siguiente puerto es " + str(port))
	servidor = nodoN(myIp, ip, port)

	
if __name__ == '__main__':
	main()


