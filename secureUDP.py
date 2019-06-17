import socket

class secureUDP():
	
	def __init__(self, ip = "", puerto = 0): #constructor
		self.SN = 0;
		self.recibidos = []
		self.enviados = []
		self.mensajesaProcesar = []
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.sock.settimeout(1)
		self.crearSocket(ip,puerto)

	##Método que crea un socket	
	def crearSocket(self,ip,puerto):
		server = (ip,puerto)
		self.sock.bind(server)

	##Método que envía mensajes útiles	
	def send(self, datos,ip,puerto):
		serverAddress = (ip, puerto)
		msgFinal = (0).to_bytes(1, byteorder="big") + (self.SN).to_bytes(2, byteorder="big") + datos
		SN = (SN + 1) % (2**16) #para asignar SN's
		self.sock.sendto(datos, serverAddress)
		parAM = (serverAddress, msgFinal)
		#tomo lock
		enviados.append(parAM)
		#libero lock

	##Hilo que tiene un timer y cada cierto tiempo revisa la lista
	def checktoResend(self):
		while True:
			#timer
			#tomo lock
			for address, msg in enviados:
				self.sock.sendto(msg, address)
			#libero lock
			#restart timer

		
	##Hilo que esta constantemente recibiendo mensajes
	def receive(self):
		while True:
			msg, address = self.sock.recvfrom(1024) #debemos ver tamaño maximo que enviamos
			parAM = (address, msg)
			#tomo lock
			recibidos.append(parAM)
			#libero lock

	##Hilo que revisa la lista de recibidos y toma acciones necesarias
	def checkList(self):
		while True:
			recvIndex = 0
			for address, msg in recibidos: #para cada par en la lista
				index = 0
				if msg[0] == 1: #significa que el mensaje recibido es un ack procedo a buscar en la lista de enviados y borrar
					SNR =   int.from_bytes([msg[1], msg[2]], byteorder='big') #se ocupan locks por acá
					for address, msj in enviados:  #puede que haya una forma más eficiente de hacer esto en vez de recorrer todo
						SNE =  int.from_bytes([msj[1], msj[2]], byteorder='big')
						if SNE == SNR: 
							#tomo lock
							del enviados[index]
							#libero lock
						index += 1

				elif msg[0] == 0:
					mesage = bytearray([1, msg[1], msg[2]]) #no estoy segura si msg[0] como ya es un byte esto lo acepte 
					self.sock.sendto(mesage, address) #se envió ack
					self.mensajesaProcesar.append(msg[3:len(msg)]) #solo el mensaje util que debe ser procesado
				del recibidos[recvIndex] #ya tomó la acción necesaria borra el recibido

		##Método que usa la capa superior para obtener el mensaje
		def getMesage(self):
			if len(mensajesaProcesar) != 0:
				return mensajesaProcesar.pop(0) #siempre hace un pop del primero y lo borra