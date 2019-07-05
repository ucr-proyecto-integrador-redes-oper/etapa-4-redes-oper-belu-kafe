from secureUDP import secureUDP
from Util import str_ip_to_tuple, ip_to_bytes, ip_tuple_to_str, ip_to_int_tuple
import sys
import socket
import csv
from threading import Lock, Thread
from time import sleep
from ipaddress import*
import re # Para usar RegEx (Expresiones Regulares)

class nodoN():

	# constructor de la clase nodo
	def __init__(self, myIp ,ip, port):  # constructor
		self.ORANGE_PORT = 9999
		self.BLUE_PORT = 19999
		self.TOKEN_INICIAL = 0
		self.TOKEN_OCUPADO = 1
		self.TOKEN_COMPLETE = 2
		self.TOKEN_VACIO = 3
		self.NUM_NARANJAS = 3
		self.NUM_NARANJAS = 2
		self.NUM_AZULES = 15
		self.READYTOJOIN = 17
		self.NUM_COMPLETES = 0
		self.hostname = socket.gethostname()
		self.localIP = myIp
		self.nextOrangeIp = ip
		self.nextOrangePort = int(port)
		self.nextOrangeAddress = (self.nextOrangeIp, self.nextOrangePort)
		self.list = []
		self.cola = []
		self.listaNaranjas = []
		self.listaAzules = []
		self.ipGenerador = False
		self.socketNN = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.socketNN.bind((self.localIP, self.ORANGE_PORT))
		self.mapa = {}  # mapa que recibe key como string y una tupla de ip y puerto
		self.secureUDPBlue = secureUDP(self.localIP, self.BLUE_PORT)
		input("Presione enter para iniciar proceso.")
		self.cargarArchivo()
		self.enviarPaqIniciales(self.localIP)
		hiloRecvNaranja = Thread(target=self.recibirNaranja, args=())
		hiloRecvAzul = Thread(target=self.recibirSolicitud, args=())
		hiloCheckComplete = Thread(target=self.checkComplete, args=())
		hiloRecvNaranja.start()
		hiloRecvAzul.start()
		hiloCheckComplete.start()

	# Metodo cargar archivo en una lista de listas desde los argumentos
	# y la primera posicion es el nombre del nodo seguido de sus vecinos
	def cargarArchivo(self):
		archivo = "grafo.csv"
		with open(archivo) as csvarchivo:
			entrada = csv.reader(csvarchivo, delimiter=',')
			for dato in entrada:
				self.mapa[str(dato[0])] = (0,0) #Se agregan nodos al mapa, con tupla vacia
				vecinos = []
				for vecino in dato:
					if(vecino != 0):
						vecinos.append(vecino)
				self.list.append(vecinos)

	#metodo que procesa tokens según su tipo
	def recibirNaranja(self):
		while True:
			try:
				msg, address = self.socketNN.recvfrom(1024)
				tipoMensaje = int(msg[0])
				if tipoMensaje == self.TOKEN_INICIAL:
					self.procesoInicial(msg)
				if tipoMensaje == self.TOKEN_VACIO:
					nodoId = self.recibirTokenVacio()
					if nodoId == -1:
						self.sendTokenVacio()
					else:
						print("Recibi token vacio y asigne a " + str(nodoId))
						self.sendTokenOcupado(nodoId)
				if tipoMensaje == self.TOKEN_OCUPADO:
					print("Recibi token ocupado.")
					self.recibirTokenOcupado(msg)
				if tipoMensaje == self.TOKEN_COMPLETE:
					self.NUM_COMPLETES += 1
				if self.NUM_AZULES == 0: #Si ya asigné todos mis azules
					self.enviarPaqComplete()
			except socket.timeout:
				if self.ipGenerador == True:
					print("Token perdido, creando uno nuevo.")
					self.crearToken()

	def procesoInicial(self, msg):
		ipNaranja = ip_tuple_to_str(ip_to_int_tuple(msg[1:5]))
		print("Recibí el token inicial con IP " + ipNaranja)
		if ipNaranja != self.localIP:
			self.listaNaranjas.append(ipNaranja)
			if self.NUM_NARANJAS != 1:
				self.enviarPaqIniciales(ipNaranja)
			if len(self.listaNaranjas) == self.NUM_NARANJAS-1:
				self.compararIpsNaranjas()

	#metodo que envia la ip del naranja actual para determinar cual será el nodo generador
	def enviarPaqIniciales(self, ipNaranja):
		miDireccion = ipNaranja.split(".")
		msg = (0).to_bytes(1, byteorder="big")
		IP = ip_to_bytes(str_ip_to_tuple(ipNaranja))
		self.socketNN.sendto(msg + IP, self.nextOrangeAddress)

	#metodo que compara las ips de los naranjas para determinar cual empieza a con la asignación
	def compararIpsNaranjas(self):
		miIp = int(IPv4Address(self.localIP))
		for naranja in self.listaNaranjas:
			lAux = int(IPv4Address(naranja))
			if miIp < lAux:
				self.ipGenerador = True
				continue
			else:
				self.ipGenerador = False
				break

		if self.ipGenerador == True:
			print("Soy nodo generador")
			self.socketNN.settimeout(60)
			self.crearToken()
		else:
			print("No soy nodo generador")
			self.socketNN.settimeout(30)
			#hago asignaciones, mando token ocupado

	def crearToken(self):
		nodoId = self.recibirTokenVacio()
		if nodoId == -1:
			self.sendTokenVacio()
		else:
			self.sendTokenOcupado(nodoId)

	def sendTokenVacio(self):
		tipoMensaje = (3).to_bytes(1,"big")
		self.socketNN.sendto(tipoMensaje, self.nextOrangeAddress)

	def recibirTokenVacio(self):
		if(len(self.cola) != 0):
			solicitud = self.cola.pop(0)
			nodoId = int(self.getNodoId())
			self.actualizarEstructuras(nodoId, solicitud[0], solicitud[1])
			print(self.mapa)
			nodoIdBytes = nodoId.to_bytes(2,"big")
			vecinos = self.listaVecinos(nodoId)
			NUM_AZULES -= 1
			listaAzules.append(solicitud)
			for n in vecinos:
				if self.mapa[n] == (0,0):
					msgId = (15).to_bytes(1, "big")
					vecinoBytes = int(n).to_bytes(2,"big")
					paqueteFinal = msgId + nodoIdBytes + vecinoBytes
					self.secureUDPBlue.send(paqueteFinal, solicitud[0], solicitud[1])
				else:
					msgId = (16).to_bytes(1, "big")
					vecinoBytes = int(n).to_bytes(2,"big")
					vecinoIP = ip_to_bytes(str_ip_to_tuple(self.mapa[str(n)][0]))
					vecinoPort = self.mapa[str(n)][1].to_bytes(2, "big")
					paqueteFinal = msgId + nodoIdBytes + vecinoBytes + vecinoIP + vecinoPort
					self.secureUDPBlue.send(paqueteFinal, solicitud[0], solicitud[1])
			return nodoId
		else:
			return -1

	#Id=1 token ocupado con solicitud + nodo+ IP azul+ puerto azul
	def sendTokenOcupado(self, nodoId):
		#Si soy el generador, cambio temporalmente el timeout para este método
		if self.ipGenerador == True:
			self.socketNN.settimeout(10)
		recibido = False
		#Armo el paquete
		msgId = (1).to_bytes(1, "big")
		nodoIdBytes = nodoId.to_bytes(2,"big")
		ipAzul = ip_to_bytes(str_ip_to_tuple(self.mapa[str(nodoId)][0]))
		portAzul = (self.mapa[str(nodoId)][1]).to_bytes(2, byteorder="big")
		msgFinal = msgId + nodoIdBytes + ipAzul + portAzul
		#Mientras no reciba respuesta
		while not recibido:
			#Envío el token ocupado
			self.socketNN.sendto(msgFinal, self.nextOrangeAddress)
			try:
				#Intento recibir respuesta
				resp, address = self.socketNN.recvfrom(1024)
				nodoIdResp = int.from_bytes(resp[1:3], byteorder='big')
				if nodoId == nodoIdResp:
					recibido = True
					self.sendTokenVacio()
			except socket.timeout:
				#Si se vence el timeout, vuelvo a enviarlo
				pass
		#Si soy el generador, regreso el timeout al tiempo original
		if self.ipGenerador == True:
			self.socketNN.settimeout(60)

	def recibirTokenOcupado(self, msg):
		nodoId = int.from_bytes(msg[1:3], byteorder='big')
		ip = ip_tuple_to_str(ip_to_int_tuple(msg[3:7]))
		port = int.from_bytes(msg[7:9], byteorder='big')
		print("Actualizando lista para " + str(nodoId) + " con IP " + ip + " y " + str(port))
		self.actualizarEstructuras(nodoId, ip, port)
		self.socketNN.sendto(msg, self.nextOrangeAddress)

	#metodo que envía el paquete Complete entre los demás naranjas
	def enviarPaqComplete(self):
		#Si soy el generador, cambio temporalmente el timeout para este método
		if self.ipGenerador == True:
			self.socketNN.settimeout(10)
		recibido = False
		#Armo el paquete
		msg = (self.TOKEN_COMPLETE).to_bytes(1, byteorder="big")
				#Mientras no reciba respuesta
		while not recibido:
			self.socketNN.sendto(msg, (self.nextOrangeIp, self.nextOrangePort))
			try:
				resp, address = self.socketNN.recvfrom(1024)
				recibido = True
				self.sendTokenVacio()
			except socket.timeout:
				#Si se vence el timeout, vuelvo a enviarlo
				pass
		#Si soy el generador, regreso el timeout al tiempo original
		if self.ipGenerador == True:
			self.socketNN.settimeout(60)

	def recibirSolicitud(self):
				while True:
						msg = self.secureUDPBlue.getMessage()
						ip = ip_tuple_to_str(ip_to_int_tuple(msg[1:5]))
						port = int.from_bytes(msg[5:7], byteorder='big')
						info = ip, port
						if self.isRepeated(ip, port) == False:
							self.cola.append(info)

	def isRepeated(self, ip, port):
		for x, y in self.mapa.items():
			if y == (ip, port):
				return True
		return False

	# metodo que devuelve una lista de los vecinos solicitados
	def listaVecinos(self, nodo):
		vecinos = []
		indice = 0
		for reg in self.list:
			if int(reg[0]) == nodo:
				break
			indice += 1

		for dato in self.list[indice]:
			if dato !='' and dato != str(nodo):
				vecinos.append(dato)
		#print(vecinos)
		return vecinos

	def getNodoId(self):
		for x, y in self.mapa.items():
			if y == (0,0):
				return x

	def actualizarEstructuras(self, key, ip, puerto):
		self.mapa[str(key)] = (ip, puerto)

	def checkComplete(self):
		while True:
			if (self.NUM_AZULES == 0 and self.NUM_COMPLETES == 5):
				self.readyToJoin()

	def readyToJoin(self):
			for element in self.listaAzules:
				self.secureUDPBlue.send((self.READYTOJOIN).to_bytes(1, byteorder='big'), element[0], element[1])


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
	#servidor.recibirSolicitud()
	#servidor.actualizarEstructuras("9", "1.1.1.1", "5555")
	#servidor.enviarPaqIniciales("127.0.1.1")
	# servidor.listaNaranjas = ["127.3.5.100", "127.0.1.2", "127.0.1.5"]
	# servidor.compararIpsNaranjas()

if __name__ == '__main__':
	main()
