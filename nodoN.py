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
	# constructor de la clase nodo
	def __init__(self, ip, port):  # constructor
		self.hostname = socket.gethostname()
		self.localIP = socket.gethostbyname(self.hostname)
		self.nextOrangeIp = ip
		self.nextOrangePort = port
		self.list = []
		self.cola = []
		self.listaNaranjas = []
		##############Para obtener el nodo generador###################
		self.socketNN = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.lockRecibirPaqsIniciales = Lock()
		self.nextOrange = (self.nextOrangeIp, self.nextOrangePort)
		self.socketNN.bind(self.nextOrange)

		###############################################################
		self.mapa = {}  # mapa que recibe key como string y una tupla de ip y puerto
		self.secureUDPOrange = secureUDP(self.localIP, self.ORANGE_PORT)
		self.secureUDPBlue = secureUDP(self.localIP, self.BLUE_PORT)
		self.cargarArchivo()
		print(self.localIP)

	# Metodo cargar archivo en una lista de listas desde los argumentos
	# y la primera posicion es el nombre del nodo seguido de sus vecinos
	def cargarArchivo(self):
		archivo = ""
		if len(sys.argv) >= 2:
			archivo = sys.argv[1]
		else:
			archivo = "grafo.csv"
			print("Se usará el nombre predeterminado grafo.csv");
		with open(archivo) as csvarchivo:
			entrada = csv.reader(csvarchivo, delimiter=',')
			for dato in entrada:
				self.mapa[str(dato[0])] = () #Se agregan nodos al mapa, con tupla vacía
				vecinos = []
				for vecino in dato:
					if(vecino != 0):
						vecinos.append(vecino)
				self.list.append(vecinos)
		# Debugging
		# for r in range(len(self.list)):
		# 	print(self.list[r])
		#print(self.list)

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

	def recibirToken(self):
		while True:
			msg = secureUDPOrange.receive()
			if msg[0] == "I":
				# self.tokenInicial(msg)
				pass
			elif msg[0] == "T":
				# self.token(msg)
				pass

	def tokenInicial(self, tokenInicial):
		pass

	def token(self, token):
		pass
	
	def enviarPaqIniciales(self, ipNaranja): #Para definir el nodo generador
		miDireccion = ipNaranja.split(".")
		msg = (TOKEN_INICIAL).to_bytes(1, byteorder="big") + (int(miDireccion[0])).to_bytes(1, byteorder="big") + (int(miDireccion[1])).to_bytes(1, byteorder="big") + (int(miDireccion[2])).to_bytes(1, byteorder="big") + (int(miDireccion[3])).to_bytes(1, byteorder="big")
		self.socketNN.sendto(msg, (self.nextOrangeIp, self.nextOrangePort))


	def recibirPaqsIniciales(self):
		#esperar a recibir 5 paquetes
		while True:
			msg, address = socketNN.recvfrom(1024)
			tipoMensaje = int.from_bytes(msg[0], byteorder='big')
			if tipoMensaje == TOKEN_INICIAL:
				ipNaranja = ip_tuple_to_str(ip_to_int_tuple(msg[1:4]))

			self.lockRecibirPaqsIniciales.acquire()
			if ipNaranja != self.localIP:
				listaNaranjas.append(ipNaranja)
				self.enviarPaqIniciales(ipNaranja)

			if len(self.listaNaranjas) == 5:
				self.lockRecibirPaqsIniciales.release()
				break
			self.lockRecibirPaqsIniciales.release()

		self.compararIpsNaranjas()

	def compararIpsNaranjas(self):
		#seleccionar la ip menor menor
		soyIpMenor = False
		miIp = self.localIP.split(".")
		for naranja in self.listaNaranjas:
			lAux = naranja.split(".")
			if int(miIp[0]) < int(lAux[0]):
				soyIpMenor = True
				continue
			elif int(miIp[0]) == int(lAux[0]):
				if int(miIp[1]) < int(lAux[1]):
					soyIpMenor = True
					continue
				elif int(miIp[1]) == int(lAux[1]):
					if int(miIp[2]) < int(lAux[2]):
						soyIpMenor = True
						continue
					elif int(miIp[2]) == int(lAux[2]):
						if int(miIp[3]) < int(lAux[3]):
							soyIpMenor = True
							continue
						elif int(miIp[3]) == int(lAux[3]):
							if int(miIp[4]) < int(lAux[4]):
								soyIpMenor = True
						else: 
							soyIpMenor = False
							break
					else:
						soyIpMenor = False
						break
				else:
					soyIpMenor = False
					break
			else:
				soyIpMenor = False
				break
		
		if soyIpMenor:
			#hago asignaciones, mando token ocupado
			pass
		# si no no hago nada
		pass

	def recibirSolicitud(self):
		while True:
			msg = self.secureUDPBlue.getMessage()
			print("¡Got request!")
			ip = ip_tuple_to_str(ip_to_int_tuple(msg[0:4]))
			port = int.from_bytes(msg[4:6], byteorder='big')
			info = ip, port
			print(info)
			self.secureUDPBlue.send(str.encode("Hola"), ip, port)
			break
			cola.append(info)

	def actualizarEstructurasEstructuras(self, key, ip, puerto):
		self.mapa[key] = (ip, puerto)
		# print(self.mapa)
		vecinosNodo = self.listaVecinos(key)
		# print (vecinosNodo)
		#falta empaquetar esta información y pasarla a azules

		

def main():
	servidor = nodoN('127.0.0.0',9999)
	#servidor.recibirSolicitud()
	#servidor.actualizarEstructuras("9", "1.1.1.1", "5555")
	#servidor.enviarPaqIniciales("127.0.1.1")
	# servidor.listaNaranjas = ["127.3.5.100", "127.0.1.2", "127.0.1.5"]
	# servidor.compararIpsNaranjas()
	
if __name__ == '__main__':
	main()
