import socket
from Util import str_ip_to_tuple, ip_to_bytes, ip_tuple_to_str, ip_to_int_tuple
from struct import *
from secureUDP import secureUDP
import random
from threading import Lock, Thread
from time import sleep
import sys # Para pasar argumentos
import re # Para usar RegEx (Expresiones Regulares)
import os

class ClientNode():

	def __init__(self, myIp ,serverIP, serverPort):
		self.DEPOSITAR = 0
		self.HELLO = 1
		self.EXIST = 2 #exist solo posee el id de archivo
		self.REXIST = 3 #respuesta a exist solo posee id de archivo
		self.JOINTREE = 11
		self.IDO = 12
		self.DADDY = 13
		self.STARTJOIN = 17
		self.COMPLETEREQ = 4 #tipo de solicitud complete
		self.CARPETA = "Archivos"
		self.localIP = myIp
		self.localPort = random.randint(10000, 65000)
		self.serverIP = serverIP
		self.serverPort = serverPort
		self.secureUDP = secureUDP(self.localIP, self.localPort)
		self.nodoId = 0
		self.vecinos = []
		self.connected = 0 # variable que dice si estoy conectado al joinTree
		self.idVecinosArbol = [] #solo contiene los id se deben buscar en vecinos el ip y puerto correspondientes
		self.sendRequest()
		hiloConsola = Thread(target=self.consola, args=())
		hiloConsola.start()
		hiloRecvAzul = Thread(target=self.receive, args=())
		hiloRecvAzul.start()

	def sendRequest(self):
		msgId = (14).to_bytes(1, byteorder="big")
		msgIP = ip_to_bytes(str_ip_to_tuple(self.localIP))
		msgPort = (self.localPort).to_bytes(2, byteorder="big")
		msgFinal = (msgId + msgIP + msgPort)
		print("Sending request...")
		self.secureUDP.send(msgFinal, self.serverIP, self.serverPort)
		#Debugging splitting(should be on Orange Node)

	def receive(self):
		print("mi puerto: " + str(self.localPort))
		while True:
			infoNodo, address = self.secureUDP.getMessage()
			msgId = int(infoNodo[0])
			if int(msgId) == self.DEPOSITAR:
				accion = random.randint(0, 100)
				if accion < 60:#si accion es par va a enviar y depositar
					tamano = len(self.vecinos)-1
					vecinoEnvio = random.randint(0, tamano)#envia a un vecino random
					self.secureUDP.send(infoNodo, self.vecinos[vecinoEnvio][1], self.vecinos[vecinoEnvio][2])# envía el mismo mensaje a un vecino random
					self.depositar(infoNodo)
				else:
					self.depositar(infoNodo)
			elif int(msgId) == self.HELLO:
				vecinoId = int.from_bytes(infoNodo[1:3], "big")
				vecinoIP = ip_tuple_to_str(ip_to_int_tuple(infoNodo[3:7]))
				vecinoPort = int.from_bytes(infoNodo[7:9],"big")
				print("Actualizando vecino " + str(vecinoId) + " con IP " + vecinoIP + " con puerto " + str(vecinoPort))
				self.actualizarVecinos(vecinoId, vecinoIP, vecinoPort)
			elif int(msgId) == 15: #YOUR GRAPH POSITION cuando no hay info del vecino
				self.nodoId = int.from_bytes(infoNodo[1:3], "big")
				vecino = int.from_bytes(infoNodo[3:5],"big")
				print("Recibí vecino con ID " + str(vecino) + "no levantado.")
				if self.isRepeated(vecino) == False:
					vecino = [vecino, 0, 0]
					self.vecinos.append(vecino)
			elif int(msgId) == 16: #YOUR GRAPH POSITION cuando hay info del vecino
				self.nodoId = int.from_bytes(infoNodo[1:3], "big")
				vecino = int.from_bytes(infoNodo[3:5],"big")
				print("Recibí vecino con ID " + str(vecino) + "ya levantado.")
				vecinoIP = ip_tuple_to_str(ip_to_int_tuple(infoNodo[5:9]))
				vecinoPort = int.from_bytes(infoNodo[9:11],"big")
				if self.isRepeated(vecino) == False:
					vecino = [vecino, vecinoIP, vecinoPort]
					self.vecinos.append(vecino)
				print("Enviando Hello a " + str(vecino))
				self.helloVecino(vecinoIP, vecinoPort)
			elif int(msgId) == self.JOINTREE:#si recibo solicitud de unión respondo si estoy en el arbol
				idSolicitud = int.from_bytes(infoNodo[1:3], "big")
				self.Ido(idSolicitud)
			elif int(msgId) == self.IDO:#si recibo un IDO veo si estoy conectado y si no envío un daddy y agrego a mi papa a la lista idVecinosArbol
				if self.connected == 0:
					self.daddy()
					idPadre= int.from_bytes(infoNodo[1:3], "big")
					print("Me he unido al grafo mi ID: " + str(self.nodoId) +" el ID de mi padre: " +  str(idPadre))
					self.idVecinosArbol.append(idPadre)
			elif int(msgId) == self.DADDY:#si recibo un daddy agrego el id del nodo a mi lista de idVecinosArbol
				idHijo= int.from_bytes(infoNodo[1:3], "big")
				self.idVecinosArbol.append(idHijo)
			elif int(msgId) == self.STARTJOIN:##un mensaje con solo ese numero que viene de los naranjas a todos los azules que asignó para que comiencen a unirse al grafo, cuando un nodo azul recibe esto pone a correr el hilo joinTree.
				self.startJoin()
			elif int(msgId) == self.COMPLETEREQ:
				#if(self.existe()):
				idArchivo = int.from_bytes(infoNodo[1:3], "big")
				print("Revisando si el archivo está completo...")
				self.completo(idArchivo)

	def exist(self, mensaje):
		identArchivo = int.from_bytes(mensaje[1:4], "big")
		idnodoFile = self.CARPETA + "/" + str(self.nodoId)
		direccion = idnodoFile + "/" + str(identArchivo)
		if os.path.exists(direccion):
			print("si existe archivo...")
			return True
		else:
			return False

	def depositar(self, mensaje): ##si tiene que depositar mensaje se va a la carpeta Archivos en esta carpeta abran otras carpetas las cuales se
		#identifican con el id de nodo, y luego otras con identificador de archivo si la carpeta existe solo añade el nuevo chunk
		#sino existe crea la carpeta y añade el archivo con el chunk
		identArchivo = int.from_bytes(mensaje[1:4], "big")
		numeroChunk = int.from_bytes(mensaje[4:8], "big")
		idnodoFile = self.CARPETA + "/" + str(self.nodoId)
		if os.path.exists(idnodoFile) == False:
			 os.mkdir(idnodoFile)
		direccion = idnodoFile + "/" + str(identArchivo)
		nombreArchivoNuevo = direccion + "/" + str(numeroChunk) + ".txt"
		chunk = mensaje[8:len(mensaje)]
		if os.path.exists(direccion):
			file = open(nombreArchivoNuevo, "w")
			file.write(chunk.decode('utf-8'))
			file.close()
		else:
			os.mkdir(direccion)
			file = open(nombreArchivoNuevo, "w")
			file.write(chunk.decode('utf-8'))
			file.close()

	def joinTree(self): ##envía un mensaje a sus vecinos azules para ver si logra conectarse al arbol de expansión minima(DEBE SER UN HILO)
		if self.nodoId == 1: #si yo soy el nodo que por defecto ya estoy en el árbol no tengo que intentar unirme
			self.connected = 1 #pongo mi variable connected como 1
			return 0
		while self.connected == 0:
			msgId = (self.JOINTREE).to_bytes(1, byteorder="big")
			nodeId = (self.nodoId).to_bytes(2, byteorder="big")
			msgFinal = (msgId + nodeId)
			for vecino in self.vecinos :
				self.secureUDP.send(msgFinal, vecino[1], int(vecino[2]))
			sleep(5)

	def Ido(self, Idnodo): #se envía mensaje si formo parte del árbol
		if self.connected == 1:
			msg = (self.IDO).to_bytes(1, byteorder="big") + (self.nodoId).to_bytes(2, byteorder="big")
			for elemento in self.vecinos:
				if elemento[0] == Idnodo :
					self.secureUDP.send(msg, elemento[1], int(elemento[2])) #envia un msj de IDO a otro azul

	def daddy(self):#Envio un mensaje para avisarle al nodo que escogí para unirme al arbol de expansión minima
		msg = (self.DADDY).to_bytes(1, byteorder="big") + (self.nodoId).to_bytes(2, byteorder="big")
		self.connected == 1

	def startJoin(self):
		print("Starting... joinTree")
		hiloJoin = Thread(target=self.joinTree, args=())
		hiloJoin.start()


	def helloVecino(self, vecinoIP, vecinoPort):
		msgId = (1).to_bytes(1, byteorder="big")
		nodoId = (self.nodoId).to_bytes(2, byteorder="big")
		msgIP = ip_to_bytes(str_ip_to_tuple(self.localIP))
		msgPort = (self.localPort).to_bytes(2, byteorder="big")
		msgFinal = (msgId + nodoId + msgIP + msgPort)
		self.secureUDP.send(msgFinal, vecinoIP, vecinoPort)

	def actualizarVecinos(self, vecinoId, vecinoIP, vecinoPort):
		for vecino in self.vecinos:
			if vecino[0] == vecinoId:
				vecino[1] = vecinoIP
				vecino[2] = vecinoPort

	def isRepeated(self, nodoId):
		for n in self.vecinos:
			if n[0] == nodoId:
				return True
		return False

	def consola(self):
		while True:
			resp = input()
			if resp == "1":
				print("Yo soy " + str(self.nodoId) + " con IP " + self.localIP + " y puerto " + str(self.localPort))
				for n in self.vecinos:
					print(n)

	def completo(self, idArchivo):
		pass
		#Como sabe el azul la cantidad de chunks que tiene un archivo 

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
