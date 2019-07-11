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
		self.COMPLETE = 4 #tipo de solicitud complete
		self.RCOMPLETE = 5 #respuesta a complete
		self.OBTENER = 6 #Get
		self.ROBTENER = 7 #Respuesta Get
		self.LOCALIZAR = 8
		self.RLOCALIZAR = 9
		self.DELETE = 10
		self.JOINTREE = 11
		self.IDO = 12
		self.DADDY = 13
		self.STARTJOIN = 17
		self.CARPETA = "Archivos"
		self.localIP = myIp
		self.localPort = random.randint(10000, 65000)
		self.serverIP = serverIP
		self.serverPort = serverPort
		self.secureUDP = secureUDP(self.localIP, self.localPort)
		self.max_diff_requests = 5
		self.nodoId = 0
		self.vecinos = []
		self.connected = 0 # variable que dice si estoy conectado al joinTree
		self.idVecinosArbol = [] #solo contiene los id se deben buscar en vecinos el ip y puerto correspondientes
		self.sendRequest()
		self.ip_reply_obtener = 0 #para guardar la ip del verde solicitante del obtener
		self.port_reply_obtener = 0 #para guardar el puerto del verde solicitante del obtener
		self.reqListLocate = []
		self.reqListExiste = []
		self.reqListObtener = []
		self.reqListComplete = []
		self.ID_ARCHIVO_OBTENER = 0 #Para poder llamar al processList cuando recibí una respuesta de obtener
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
					idPadre = int.from_bytes(infoNodo[1:3], "big")
					self.daddy(idPadre)
					print("Me he unido al grafo mi ID: " + str(self.nodoId) +" el ID de mi padre: " +  str(idPadre))
					self.idVecinosArbol.append(idPadre)

			elif int(msgId) == self.DADDY:#si recibo un daddy agrego el id del nodo a mi lista de idVecinosArbol
				idHijo= int.from_bytes(infoNodo[1:3], "big")
				self.idVecinosArbol.append(idHijo)

			elif int(msgId) == self.STARTJOIN:##un mensaje con solo ese numero que viene de los naranjas a todos los azules que asignó para que comiencen a unirse al grafo, cuando un nodo azul recibe esto pone a correr el hilo joinTree.
				self.startJoin()

			elif int(msgId) == self.OBTENER:
				self.ID_ARCHIVO_OBTENER = int.from_bytes(infoNodo[1:3], "big")
				print("Procediendo a obtener el archivo con id ", self.ID_ARCHIVO_OBTENER)
				ip_in = int.from_bytes(address[0:4], "big") #ip del nodo proveniente
				puerto_in = int.from_bytes(address[4:5], "big") #puerto del nodo proveniente
				self.obtener(self.ID_ARCHIVO_OBTENER, ip_in, puerto_in)

			elif int(msgId) == self.ROBTENER:
				self.processList(self.reqListObtener, self.ID_ARCHIVO_OBTENER)
				self.secureUDP.send(infoNodo, self.ip_reply_obtener, self.port_reply_obtener)

			elif int(msgId) == self.COMPLETE:
				#if(self.exist()):
				idArchivo = int.from_bytes(infoNodo[1:4], "big")
				print("Revisando si el archivo está completo...")
				self.completo(idArchivo, address[0], address[1])

			elif int(msgId) == self.RCOMPLETE:
				idArchivo = int.from_bytes(infoNodo[1:4], "big")
				chunkNum = int.from_bytes(infoNodo[4:8], "big")
				self.respuestaComplete(chunkNum, idArchivo)

			elif int(msgId) == self.LOCALIZAR:
				idArchivo = int.from_bytes(infoNodo[1:4], "big")
				print("Solicitud de localizar de archivo " + str(idArchivo))
				self.localizar(idArchivo, address[0], address[1])

			elif int(msgId) == self.RLOCALIZAR:
				idArchivo = int.from_bytes(infoNodo[1:4], "big")
				nodoId = int.from_bytes(infoNodo[4:6], "big")
				print("Localizado el archivo " + str(idArchivo) + " en el nodo " + str(nodoId))
				self.respuestaLocalizar(nodoId, idArchivo)

			elif int(msgId) == self.EXISTE:
				if exist(infoNodo) == True:
					msg = (self.REXIST).to_bytes(1, byteorder="big") + infoNodo[1:4]
					self.secureUDP.send(msg, address[0], address[1]);
				else:
					msgExiste(infoNodo, address[0], address[1])

			elif  int(msgId) == self.REXISTE:
				idArchivo = int.from_bytes(infoNodo[1:4], "big")
				self.processList(self.reqListExiste, idArchivo)

			elif  int(msgId) == self.DELETE:
				idArchivo = int.from_bytes(infoNodo[1:4], "big")
				delete(idArchivo)

	def delete(self, idArchivo):
		idnodoFile = self.CARPETA + "/" + str(self.nodoId)
		direccion = idnodoFile + "/" + str(idArchivo)
		if os.path.exists(direccion):
			print("eliminando archivo con id " + str(idArchivo))
			os.removedirs(direccion)

	def exist(self, mensaje): #este exist no es el mismo de la solicitud EXISTE
		identArchivo = int.from_bytes(mensaje[1:4], "big")
		idnodoFile = self.CARPETA + "/" + str(self.nodoId)
		direccion = idnodoFile + "/" + str(identArchivo)
		if os.path.exists(direccion):
			print("si existe archivo...")
			return True
		else:
			return False

	def msgExiste(self, mensaje, ip_in, puerto_in):
		idArchivo = int.from_bytes(mensaje[1:4], "big")
		self.addRequest(self.reqListExiste, idArchivo, ip, puerto)
		for x in self.idVecinosArbol:
			ip, puerto = self.findIPPuerto(x)
			if ( ip != ip_in): # mandarselo a todos excepto del que viene
				self.secureUDP.send(mensaje, ip, puerto)


	def depositar(self, mensaje): ##si tiene que depositar mensaje se va a la carpeta Archivos en esta carpeta abran otras carpetas las cuales se
		#identifican con el id de nodo, y luego otras con identificador de archivo si la carpeta existe solo añade el nuevo chunk
		#sino existe crea la carpeta y añade el archivo con el chunk
		identArchivo = int.from_bytes(mensaje[1:4], "big")
		numeroChunk = int.from_bytes(mensaje[4:8], "big")
		idnodoFile = self.CARPETA + "/" + str(self.nodoId)
		if os.path.exists(idnodoFile) == False:
			os.makedirs(idnodoFile)
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
				self.secureUDP.send(msgFinal, str(vecino[1]), int(vecino[2]))
			sleep(1)

	def Ido(self, Idnodo): #se envía mensaje si formo parte del árbol
		if self.connected == 1:
			msg = (self.IDO).to_bytes(1, byteorder="big") + (self.nodoId).to_bytes(2, byteorder="big")
			for elemento in self.vecinos:
				if elemento[0] == Idnodo :
					self.secureUDP.send(msg, str(elemento[1]), int(elemento[2])) #envia un msj de IDO a otro azul

	def daddy(self, idNodo):#Envio un mensaje para avisarle al nodo que escogí para unirme al arbol de expansión minima
		msg = (self.DADDY).to_bytes(1, byteorder="big") + (self.nodoId).to_bytes(2, byteorder="big")
		for elemento in self.vecinos:
				if elemento[0] == idNodo:
					self.secureUDP.send(msg, str(elemento[1]), int(elemento[2])) #envia un msj de IDO a otro azul
		self.connected = 1

	def startJoin(self):
		while True:
			cantidadDeVecinos = 0
			for vecino in self.vecinos:
				if vecino[1] != 0 and vecino[2] != 0:
					cantidadDeVecinos += 1
			if cantidadDeVecinos == len(self.vecinos):
				break
		print("Starting... joinTree")
		hiloJoin = Thread(target=self.joinTree, args=())
		hiloJoin.start()

	#Si tengo vecinos ya instanciados, les notifico que ya existo con un Hello
	def helloVecino(self, vecinoIP, vecinoPort):
		msgId = (1).to_bytes(1, byteorder="big")
		nodoId = (self.nodoId).to_bytes(2, byteorder="big")
		msgIP = ip_to_bytes(str_ip_to_tuple(self.localIP))
		msgPort = (self.localPort).to_bytes(2, byteorder="big")
		msgFinal = (msgId + nodoId + msgIP + msgPort)
		self.secureUDP.send(msgFinal, vecinoIP, vecinoPort)

	#Método que actualiza mis vecinos cuando recibo un Hello
	def actualizarVecinos(self, vecinoId, vecinoIP, vecinoPort):
		for vecino in self.vecinos:
			if vecino[0] == vecinoId:
				vecino[1] = vecinoIP
				vecino[2] = vecinoPort

	#Método que verifica si recibo un vecino repetido
	def isRepeated(self, nodoId):
		for n in self.vecinos:
			if n[0] == nodoId:
				return True
		return False

	#Hilo que recibe de consola un 1 para digitar su información de ID de nodo con sus vecinos
	def consola(self):
		while True:
			resp = input()
			if resp == "1":
				print("Yo soy " + str(self.nodoId) + " con IP " + self.localIP + " y puerto " + str(self.localPort))
				for n in self.vecinos:
					print(n)

	def findIPPuerto(self, idVecino):
			for vecino in self.vecinos:
				if vecino[0] == idVecino:
					return vecino[1], vecino[2]

	def completo(self, idArchivo, ip_in, puerto_in):
		self.addRequest(self.reqListComplete, idArchivo, ip_in, puerto_in);
		#//self.ip_reply = ip_in # guarda ip proveniente para usar en la respuesta
		#self.port_reply = puerto_in # guarda puerto proveniente para usar en la respuesta
		for x in self.idVecinosArbol:
			ip, puerto = self.findIPPuerto(x)
			if ( ip != ip_in): # mandarselo a todos excepto del que viene
				msg = (self.COMPLETE).to_bytes(1, byteorder="big") + (idArchivo).to_bytes(3, byteorder="big")
				self.secureUDP.send(msg, ip, puerto)
		direccion = os.getcwd() + "/" + self.CARPETA + "/" + str(self.nodoId) + "/" + str(idArchivo)
		listaChunks = listdir(direccion)
		tipo = (self.RCOMPLETE).to_bytes(1, byteorder="big") + (idArchivo).to_bytes(3, byteorder="big")
		for z in listaChunks:
			chunkID = (z).to_bytes(4, byteorder="big")
			msg = tipo + chunkID
			self.secureUDP.send(msg, ip_in, puerto_in) #mandar número de chunk

	def respuestaComplete(self, chunkNum, idArchivo):
		self.processList(self.reqListComplete, idArchivo)
		for request in self.reqListComplete:
			if request[0] == idArchivo:
				msg = (self.RCOMPLETE).to_bytes(1, byteorder="big") + (idArchivo).to_bytes(3, byteorder="big") + (chunkNum).to_bytes(4, byteorder="big")
				self.secureUDP.send(msg, request[1], request[2])

	#Metodo debe de hacer bcast a los demás azules, traer los chunks, sin repetir, y una vez que están todos pasarlos al verde solicitante
	def obtener(self, idArchivo, ip_in, puerto_in):
		self.addRequest(self.reqListObtener, idArchivo, ip_in, puerto_in)
		# self.ip_reply_obtener = ip_in # guarda ip proveniente para usar en la respuesta
		# self.port_reply_obtener = puerto_in # guarda puerto proveniente para usar en la respuesta
		for x in self.idVecinosArbol:
			ip, puerto = self.findIPPuerto(x)
			if ( ip != ip_in): # mandarselo a todos excepto del que viene
				msg = (self.OBTENER).to_bytes(1, byteorder="big") + (idArchivo).to_bytes(3, byteorder="big")
				self.secureUDP.send(msg, ip, puerto)
		direccion = os.getcwd() + "/" + self.CARPETA + "/" + str(self.nodoId) + "/" + str(idArchivo)
		listaChunks = os.listdir(direccion)
		tipo = (self.ROBTENER).to_bytes(1, byteorder="big") + (idArchivo).to_bytes(3, byteorder="big")
		for j in listaChunks:
			chunkID = (j).to_bytes(4, byteorder="big")
			msg = tipo + chunkID
			self.secureUDP.send(msg, ip_in, puerto_in) #mandar número de chunk ##########################################################3


	def localizar(self, idArchivo, ip_in, puerto_in):
		self.addRequest(self.reqListLocate, idArchivo, ip_in, puerto_in)
		for x in self.idVecinosArbol:
			ip, puerto = self.findIPPuerto(x)
			if ( ip != ip_in): # mandarselo a todos excepto del que viene
				msg = (self.LOCALIZAR).to_bytes(1, byteorder="big") + (idArchivo).to_bytes(3, byteorder="big")
				self.secureUDP.send(msg, ip, puerto)
		direccion = os.getcwd() + "/" + self.CARPETA + "/" + str(self.nodoId) + "/" + str(idArchivo)
		if os.path.exists(direccion) == True:
			msg = (self.RLOCALIZAR).to_bytes(1, byteorder="big") + (idArchivo).to_bytes(3, byteorder="big") + (self.nodoId).to_bytes(2, byteorder="big")
			self.secureUDP.send(msg, ip_in, puerto_in)

	def respuestaLocalizar(self, nodoId, idArchivo):
		self.processList(self.reqListLocate, idArchivo)
		for request in self.reqListLocate:
			if request[0] == idArchivo:
				msg = (self.RLOCALIZAR).to_bytes(1, byteorder="big") + (idArchivo).to_bytes(3, byteorder="big") + (nodoId).to_bytes(2, byteorder="big")
				self.secureUDP.send(msg, request[1], request[2])

	#Se llama cuando se recibe una solicitud
	def addRequest(self, reqList, idArchivo, ip, puerto):
		repeatedRequest = False

		for request in reqList:
			if request[0] == idArchivo and request[1] == ip and request[2] == puerto:
				repeatedRequest = True

		#Si no estoy en la lista, me agrego
		if repeatedRequest == False:
			req = [idArchivo, ip, puerto, 0]
			reqList.append(req)

	#Se llama cuando se recibe una respuesta de solicitud
	def processList(self, reqList, idArchivo):
		#Elementos de lista:
		#[0] : IdArchivo
		#[1] : IP del nodo azul que lo solicitó
		#[2] : Puerto del nodo azul que lo solicitó
		#[3] : Contador de cuántos paquetes se han recibido de otros idArchivo, si esto llega a 5, se descarta
		#Aumentar contador a todos las otras solicitudes diferentes del idArchivo
		for request in reqList:
			#Si no soy la solicitud, aumento contador en 1
			if request[0] != idArchivo:
				request[3] += 1
				#Si llego al máximo de contador, me elimino
				if request[3] == self.max_diff_requests:
					reqList.remove(request)
			else:
				#Si es mi solicitud, reinicio el contador
					request[3] = 0

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
