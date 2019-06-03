import socket
from secureUDP import secureUDP


class nodoN():
    ##constructor de la clase nodo
	def __init__(self, ip, puerto): #constructor
		self.ip = ip
		self.puerto = puerto
		self.list = []
		secureUDP.crearSocket(ip,puerto)

    ##Metodo cargar archivo en una lista de listas desde los argumentos
    ## y la primera posicion es el nombre del nodo seguido de sus vecinos
	def cargarArchivo():
		archivo=""
		if len(sys.argv) >= 2:
			archivo = sys.argv[1]
		else:
			print("Este programa necesita un parámetro");
			exit(0)
			with open(archivo) as csvarchivo:
				entrada = csv.reader(csvarchivo)
			for dato in entrada:
				print(dato)
				self.list.append(dato)

    ##metodo que devuelve una lista de los vecinos solicitados
	def listaVecinos(nodo):
		vecinos=[]
		for fila in list:
			if fila[0] == nodo:
				for dato in fila:
					if dato !='' and dato != nodo:
						vecinos.append(dato)
		print(vecinos)
		return vecinos


def main():
	servidor = nodoN('0.0.0.0',8888)

if __name__ == '__main__': main()
