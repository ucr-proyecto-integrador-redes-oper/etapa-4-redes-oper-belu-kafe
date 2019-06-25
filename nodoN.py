from secureUDP import secureUDP
from Util import str_ip_to_tuple, ip_to_bytes, ip_tuple_to_str, ip_to_int_tuple
import sys
import socket
import csv
from threading import Lock, Thread
from time import sleep

class nodoN():
	
	ORANGE_PORT = 9999
	BLUE_PORT = 19999
	TOKEN_INICIAL = 0
	TOKEN_OCUPADO = 1
	TOKEN_COMPLETE = 2
	TOKEN_VACIO = 3
	# constructor de la clase nodo
	def __init__(self, ip, port):  # constructor
		self.hostname = socket.gethostname()
		self.localIP = socket.gethostbyname(self.hostname)
		self.nextOrangeIp = ip
		self.nextOrangePort = port
		self.nextOrangeAddress = (self.nextOrangeIp, self.nextOrangePort)
		self.list = []
		self.cola = []
		self.listaNaranjas = []
		self.ipGenerador = False
		self.socketNN = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.socketNN.bind((self.localIP, self.ORANGE_PORT))
		self.mapa = {}  # mapa que recibe key como string y una tupla de ip y puerto
		self.secureUDPBlue = secureUDP(self.localIP, self.BLUE_PORT)
		self.cargarArchivo()
		self.enviarPaqIniciales(self.localIP)
		hiloRecvNaranja = Thread(target=self.recibirNaranja, args=())
		hiloRecvAzul = Thread(target=self.recibirSolicitud, args=())
		hiloRecvNaranja.start()
		hiloRecvAzul.start()
		print(self.localIP)

	# Metodo cargar archivo en una lista de listas desde los argumentos
	# y la primera posicion es el nombre del nodo seguido de sus vecinos
	def cargarArchivo(self):
		archivo = ""
		if len(sys.argv) >= 2:
			archivo = sys.argv[1]
		else:
			archivo = "grafo.csv"
			print("Se usara el nombre predeterminado grafo.csv")
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
		#esperar a recibir 5 paquetes
		while True:
			try:
				msg, address = socketNN.recvfrom(1024)
				tipoMensaje = int.from_bytes(msg[0], byteorder='big')
				if tipoMensaje == TOKEN_INICIAL:
					self.procesoInicial(msg)
				if tipoMensaje == TOKEN_VACIO:
					nodoId = self.recibirTokenVacio()
					if nodoId == -1:
						self.sendTokenVacio()
					else:
						self.sendTokenOcupado(nodoId)
				if tipoMensaje == TOKEN_OCUPADO:
					self.recibirTokenOcupado(msg)
				if tipoMensaje == TOKEN_COMPLETE:
					self.enviarPaqComplete()
			except socket.timeout:
				if self.ipGenerador == True:	
					print("Token perdido, creando uno nuevo.")
					self.crearToken()

	def procesoInicial(self, msg):
		ipNaranja = ip_tuple_to_str(ip_to_int_tuple(msg[1:4]))

		if ipNaranja != self.localIP:
			listaNaranjas.append(ipNaranja)
			self.enviarPaqIniciales(ipNaranja)

		if len(self.listaNaranjas) == 5:
			self.compararIpsNaranjas()

	#metodo que envia la ip del naranja actual para determinar cual será el nodo generador
	def enviarPaqIniciales(self, ipNaranja):
		miDireccion = ipNaranja.split(".")
		msg = (TOKEN_INICIAL).to_bytes(1, byteorder="big") + (int(miDireccion[0])).to_bytes(1, byteorder="big") + (int(miDireccion[1])).to_bytes(1, byteorder="big") +(int(miDireccion[2])).to_bytes(1, byteorder="big") + (int(miDireccion[3])).to_bytes(1, byteorder="big")
		self.socketNN.sendto(msg, self.nextOrangeAddress)

	#metodo que compara las ips de los naranjas para determinar cual empieza a con la asignación
	def compararIpsNaranjas(self):
		miIp = self.localIP.split(".")
		for naranja in self.listaNaranjas:
			lAux = naranja.split(".")
			if int(miIp[0]) < int(lAux[0]):
				self.ipGenerador = True
				continue
			elif int(miIp[0]) == int(lAux[0]):
				if int(miIp[1]) < int(lAux[1]):
					self.ipGenerador = True
					continue
				elif int(miIp[1]) == int(lAux[1]):
					if int(miIp[2]) < int(lAux[2]):
						self.ipGenerador = True
						continue
					elif int(miIp[2]) == int(lAux[2]):
						if int(miIp[3]) < int(lAux[3]):
							self.ipGenerador = True
							continue
						elif int(miIp[3]) == int(lAux[3]):
							if int(miIp[4]) < int(lAux[4]):
								self.ipGenerador = True
						else: 
							self.ipGenerador = False
							break
					else:
						self.ipGenerador = False
						break
				else:
					self.ipGenerador = False
					break
			else:
				self.ipGenerador = False
				break
		
		if self.ipGenerador == True:
			self.socketNN.settimeout(60)
			self.crearToken()
		else:
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
		socketNN.sendto(tipoMensaje, self.nextOrangeAddress)

	def recibirTokenVacio(self):
		if(len(cola) != 0):
			solicitud = cola.pop(0)
			nodoId = int(self.getNodoId())
			actualizarEstructuras(nodoId, solicitud[0], solicitud[1])
			nodoIdBytes = nodoId.to_bytes(2,"big")
			vecinos = listaVecinos(nodoId)
			for n in vecinos:
				if self.mapa[n] == (0,0):
					vecinoBytes = n.to_bytes(2,"big")
					paqueteFinal = nodoIdBytes + vecinoBytes
					self.secureUDPBlue.send(paqueteFinal, solicitud[0], solicitud[1])
				else:
					vecinoBytes = n.to_bytes(2,"big")
					vecinoIP = self.mapa[n][0].to_bytes(4, "big")
					vecinoPort = self.mapa[n][1].to_bytes(2, "big")
					paqueteFinal = nodoIdBytes + vecinoBytes + vecinoIP + vecinoPort
					self.secureUDPBlue.send(paqueteFinal, solicitud[0], solicitud[1])
			return nodoId
		else:
			return -1

	#Id=1 token ocupado con solicitud + nodo+ IP azul+ puerto azul
	def sendTokenOcupado(self, nodoId):
		#Si soy el generador, cambio temporalmente el timeout para este método
		if self.ipGenerador == True:
			socketNN.settimeout(10)
		recibido = False
		#Armo el paquete
		msgId = (1).to_bytes(1, "big")
		nodoIdBytes = nodoId.to_bytes(2,"big") 
		ipAzul = ip_to_bytes(str_ip_to_tuple(self.map[nodoId][0]))
		portAzul = (self.map[nodoId][1]).to_bytes(2, byteorder="big")
		msgFinal = msgId + nodoIdBytes + ipAzul + portAzul
		#Mientras no reciba respuesta
		while not recibido:
			#Envío el token ocupado
			self.socketNN.sendto(msgFinal, nextOrangeAddress)
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
			socketNN.settimeout(60)

	def recibirTokenOcupado(self, msg):
		nodoId = int.from_bytes(msg[1:3], byteorder='big')			
		ip = ip_tuple_to_str(ip_to_int_tuple(msg[3:7]))
		port = int.from_bytes(msg[7:9], byteorder='big')
		self.actualizarEstructuras(nodoId, ip, port)
		self.socketNN.sendto(msg, self.nextOrangeAddress)	

	#metodo que envía el paquete Complete entre los demás naranjas
	def enviarPaqComplete(self):
		#Si soy el generador, cambio temporalmente el timeout para este método
		if self.ipGenerador == True:
			socketNN.settimeout(10)
		recibido = False
		#Armo el paquete
		msg = (TOKEN_COMPLETE).to_bytes(1, byteorder="big") #+ (int(miDireccion[0])).to_bytes(1, byteorder="big") + (int(miDireccion[1])).to_bytes(1, byteorder="big") +(int(miDireccion[2])).to_bytes(1, byteorder="big") + (int(miDireccion[3])).to_bytes(1, byteorder="big") + (int(ipAzul[0])).to_bytes(1, byteorder="big") + (int(ipAzul[1])).to_bytes(1, byteorder="big") + (int(ipAzul[2])).to_bytes(1, byteorder="big") + (int(ipAzul[3])).to_bytes(1, byteorder="big") + (puertoAzul).to_bytes(1, byteorder="big")
				#Mientras no reciba respuesta
		while not recibido:
			socketNN.sendto(msg, (self.nextOrangeIp, self.nextOrangePort))
			try:
				resp, address = self.socketNN.recvfrom(1024)
				recibido = True
				self.sendTokenVacio()
			except socket.timeout:
				#Si se vence el timeout, vuelvo a enviarlo
				pass
		#Si soy el generador, regreso el timeout al tiempo original
		if self.ipGenerador == True:
			socketNN.settimeout(60)

	def recibirSolicitud(self):
		while True:
			msg = self.secureUDPBlue.getMessage()
			print("Got request!")
			ip = ip_tuple_to_str(ip_to_int_tuple(msg[0:4]))
			port = int.from_bytes(msg[4:6], byteorder='big')
			info = ip, port
			print(info)
			cola.append(info)

	# metodo que devuelve una lista de los vecinos solicitados
	def listaVecinos(self, nodo):
		vecinos = []
		indice = 0
		for reg in self.list:
			if reg[0] == nodo:
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
		self.mapa[key] = (ip, puerto)
		

def main():
	ip = input("Digite la IP del siguiente naranja: ")
	port = input("Digite el puerto del siguiente naranja: ")
	input("Presione enter para iniciar proceso.")
	servidor = nodoN(ip, port)
	#servidor.recibirSolicitud()
	#servidor.actualizarEstructuras("9", "1.1.1.1", "5555")
	#servidor.enviarPaqIniciales("127.0.1.1")
	# servidor.listaNaranjas = ["127.3.5.100", "127.0.1.2", "127.0.1.5"]
	# servidor.compararIpsNaranjas()
	
if __name__ == '__main__':
	main()


