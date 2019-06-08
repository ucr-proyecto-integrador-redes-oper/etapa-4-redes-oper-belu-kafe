from secureUDP import secureUDP
from Util import str_ip_to_tuple, ip_to_bytes, ip_tuple_to_str, ip_to_int_tuple
import sys
import csv


class nodoN():
	hostname = socket.gethostname()
	localIP = socket.gethostbyname(hostname)
	localPort = 2019
	ORANGE_PORT = 9999
	BLUE_PORT = 19999
    # constructor de la clase nodo
	def __init__(self, ip, puerto):  # constructor
		self.ip = ip
		self.puerto = puerto
		self.list = []
		self.cola = []
		self.mapa = {}  # mapa que recibe key como string y una tupla de ip y puerto
		self.secureUDPOrange = secureUDP(self.localIP, self.ORANGE_PORT)
		self.secureUDPBlue = secureUDP(self.localIP, self.BLUE_PORT)
		self.cargarArchivo()

    # Metodo cargar archivo en una lista de listas desde los argumentos
    # y la primera posicion es el nombre del nodo seguido de sus vecinos
	def cargarArchivo(self):
		archivo = ""
		if len(sys.argv) >= 2:
			archivo = sys.argv[1]
		else:
			print("Este programa necesita un parámetro");
			exit(0)
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
		print(self.mapa)

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
	
	def recibirSolicitud(self):
		while True:
			msg = secureUDPBlue.receive()
			cola.append(msg)

	def actualizarEstructuras(self, key, ip, puerto):
		self.mapa[key] = (ip, puerto)
		# print(self.mapa)
		vecinosNodo = self.listaVecinos(key)
		# print (vecinosNodo)
		#falta empaquetar esta información y pasarla a azules

		

def main():
	servidor = nodoN('0.0.0.0',8888)
	#servidor.actualizarEstructuras("9", "1.1.1.1", "5555")
	
if __name__ == '__main__': main()
