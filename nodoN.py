from secureUDP import secureUDP
import sys
import csv

class nodoN():
	ORANGE_PORT = 9999
	BLUE_PORT = 19999
    ##constructor de la clase nodo
	def __init__(self, ip, puerto): #constructor
		self.ip = ip
		self.puerto = puerto
		self.list = []
		self.mapa = {} #mapa que recibe key como string y una tupla de ip y puerto
		self.secureUDP = secureUDP(self.ip, self.puerto)
		self.cargarArchivo()

    ##Metodo cargar archivo en una lista de listas desde los argumentos
    ## y la primera posicion es el nombre del nodo seguido de sus vecinos
	def cargarArchivo(self):
		archivo=""
		if len(sys.argv) >= 2:
			archivo = sys.argv[1]
		else:
			print("Este programa necesita un parámetro");
			exit(0)
		with open(archivo) as csvarchivo:
			entrada = csv.reader(csvarchivo, delimiter=',')
			for dato in entrada:
				vecinos = []
				for vecino in dato:
					if(vecino != 0):	
						vecinos.append(vecino)
				self.list.append(vecinos)
		#Debugging
		for r in range(len(self.list)):
			print(self.list[r])

    ##metodo que devuelve una lista de los vecinos solicitados
	def listaVecinos(self, nodo):
		vecinos=[]
		for dato in self.list[nodo-1]:
			if dato !='' and dato != str(nodo):
				vecinos.append(dato)
				self.mapa[str(dato[0])] = () #se agrega al mapa con la tupla vacía
		print(vecinos)
		return vecinos

	def recibirToken(self):
		while True:
			msg = secureUDP.receive(ORANGE_PORT)
			if msg[0] == "I":
				#tokenInicial(msg)
			elif msg[0] == "T":
				#token(msg)

	def tokenInicial(self, tokenInicial):
		pass

	def token(self, token):
		pass

	def actualizarEstructuras(key, ip, puerto):
		self.mapa[key] = (ip, puerto)

def main():
	servidor = nodoN('0.0.0.0',8888)

if __name__ == '__main__': main()
