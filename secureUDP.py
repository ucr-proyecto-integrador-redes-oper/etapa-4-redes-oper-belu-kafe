import socket
from threading import Lock, Thread
from time import sleep

class secureUDP():
	
	def __init__(self, ip = "", puerto = 0): #constructor
		self.SN = 0;
		self.recibidos = []
		self.enviados = []
		self.lockRecv = Lock()
		self.lockSend = Lock()
		self.mensajesaProcesar = []
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.crearSocket(ip,puerto)
		hiloCheckResend = Thread(target=self.checktoResend, args=())
		hiloRecv = Thread(target=self.receive, args=())
		hiloCheckList = Thread(target=self.checkList, args=())
		hiloCheckResend.start()
		hiloRecv.start()
		hiloCheckList.start()

	##Metodo que crea un socket	
	def crearSocket(self,ip,puerto):
		server = (ip,puerto)
		self.sock.bind(server)

	##Metodo que envia mensajes utiles	
	def send(self, datos,ip,puerto):
		address = (ip, puerto)
		msg = (0).to_bytes(1, byteorder="big") + (self.SN).to_bytes(2, byteorder="big") + datos
		self.SN = (self.SN + 1) % (2**16) #para asignar SN's
		self.sock.sendto(msg, address)
		parAM = (address, msg)
		print("Sent " + str(msg) + " to " + str(address))
		#tomo lock
		self.lockSend.acquire()
		self.enviados.append(parAM)
		self.lockSend.release()
		#libero lock

	##Hilo que tiene un timer y cada cierto tiempo revisa la lista
	def checktoResend(self):
		while True:
			#timer
			sleep(1) #cada 30 milisegundos revisa la lista
			#tomo lock
			self.lockSend.acquire()
			for address, msg in self.enviados:
				self.sock.sendto(msg, address)
			#libero lock
			self.lockSend.release()
			#restart timer

		
	##Hilo que esta constantemente recibiendo mensajes
	def receive(self):
		while True:
			msg, address = self.sock.recvfrom(1024) #debemos ver tamaño maximo que enviamos
			print("Received " + str(msg) + " from " + str(address))
			parAM = (address, msg)
			#tomo lock
			self.lockRecv.acquire()
			self.recibidos.append(parAM)
			self.lockRecv.release()
			#libero lock

	##Hilo que revisa la lista de recibidos y toma acciones necesarias
	def checkList(self):
		while True:
			recvIndex = 0
			if len(self.recibidos) != 0:
				received = self.recibidos.pop(recvIndex)
				index = 0
				if received[1][0] == 1: #significa que el mensaje recibido es un ack procedo a buscar en la lista de enviados y borrar
					print(f"recieve 1 1 {received[1][1:4]}")
					SNR =   int.from_bytes([received[1][1], received[1][2]], byteorder='big') #se ocupan locks por acá
					print("ACK found from " + str(received[0]) + " RN: " + str(SNR))
					self.lockSend.acquire()
					for msj in self.enviados:  #puede que haya una forma más eficiente de hacer esto en vez de recorrer todo
						SNE =  int.from_bytes([msj[1][1], msj[1][2]], byteorder='big')
						if SNE == SNR: 
							#tomo lock
							del self.enviados[index]
							#libero lock
						index += 1
					self.lockSend.release()

				elif received[1][0] == 0:
					print("Message found from " + str(received[0]))
					#print(f"recieve 1 1 {received[1][1:4]}")
					message = bytearray([1, received[1][1], received[1][2]]) #no estoy segura si msg[0] como ya es un byte esto lo acepte
				
					self.sock.sendto(message, received[0]) #se envió ack
					SN = int.from_bytes([received[1][1], received[1][2]], byteorder='big')
					print("ACK sent to " + str(received[0]) + " SN: " + str(SN))
					self.mensajesaProcesar.append(received[1][3:len(received[1])]) #solo el mensaje util que debe ser procesado
	##Método que usa la capa superior para obtener el mensaje
	def getMessage(self):
		while True:
			if len(self.mensajesaProcesar) != 0:
				print("¡Message succesfully received!")
				return self.mensajesaProcesar.pop(0) #siempre hace un pop del primero y lo borra
				
				
