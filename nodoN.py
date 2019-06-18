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
		# Debugging
		# for r in range(len(self.list)):
		# 	print(self.list[r])
		print(self.list)

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
		# stop = False
		# miDireccion = self.localIP
		# msg = (1).to_bytes(1, byteorder="big") + miDireccion
		# while stop == False:
		# 	#enviamos paquete
		# 	self.socketNN.sendto(msg, self.nextOrangeIp)
		# 	#empezamos a correr el timer
		# 	stop = self.timerInicial()
		miDireccion = ipNaranja.split(".")
		msg = (0).to_bytes(1, byteorder="big") + (int(miDireccion[0])).to_bytes(1, byteorder="big") + (int(miDireccion[1])).to_bytes(1, byteorder="big") + (int(miDireccion[2])).to_bytes(1, byteorder="big") + (int(miDireccion[3])).to_bytes(1, byteorder="big") + (1).to_bytes(1, byteorder="big")
		self.socketNN.sendto(msg, (self.nextOrangeIp, self.nextOrangePort))
		# print(str(msg))
		# print(msg)
		# valor = msg.decode("utf-8")
		# print(valor)
		# print(str(valor))


	def recibirPaqsIniciales(self):
		#esperar a recibir 5 paquetes
		while True:
			msg, address = socketNN.recvfrom(1024)
			aux = (int(val)).to_bytes(6, byteorder="big")######Revisar 
			ipNaranja = str(aux) ######si 
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
							if int(miIp[4]) < int(lAux[3]):
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
				break
		
		if soyIpMenor:
			#hago asignaciones, mando token ocupado
			pass
		# si no no hago nada

	# def timerInicial(self):
	# 	while True:
	# 		sleep(180) #Esperamos 3 minutos
	# 		#pregunta si ya tiene los 5 mensajes con las ip de los otros naranjas
	# 		if len(self.listaNaranjas) == 5:
	# 			return True
	# 		else:
	# 			return False

	def recibirSolicitud(self):
		while True:
			msg = self.secureUDPBlue.getMessage()
			print("Got request!")
			ip = ip_tuple_to_str(ip_to_int_tuple(msg[0:4]))
			port = int.from_bytes(msg[4:6], byteorder='big')
			info = ip, port
			print(info)
			cola.append(info)
		# pass

	def recibirTokenVacio(self):
		if(len(cola) != 0):
			solicitud = cola.pop(0)
			nodoId = int(self.getNodoId())
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
		
					
					
				
			
	def getNodoId(self):
		for x, y in self.mapa.items():
			if y == (0,0):
				return x
		

	def actualizarEstructuras(self, key, ip, puerto):
		self.mapa[key] = (ip, puerto)
		# print(self.mapa)
		vecinosNodo = self.listaVecinos(key)
		# print (vecinosNodo)
		#falta empaquetar esta informacion y pasarla a azules

		

def main():
	servidor = nodoN('127.0.0.0',9999)
	#servidor.recibirSolicitud()
	servidor.actualizarEstructuras("9", "1.1.1.1", "5555")
	#servidor.enviarPaqIniciales("127.0.1.1")
	
if __name__ == '__main__':
	main()
