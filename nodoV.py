from secureUDP import secureUDP
from Util import str_ip_to_tuple, ip_to_bytes, ip_tuple_to_str, ip_to_int_tuple
import sys
import socket
import csv
from threading import Lock, Thread
from time import sleep
import re # Para usar RegEx (Expresiones Regulares)
import os

class nodoV():

	# constructor de la clase nodo
    def __init__(self, myIp, idV):  # constructor
        self.DEPOSITAR = 0
        self.EXISTE = 2
        self.COMPLETO = 4
        self.OBTENER = 6 #Get
        self.LOCALIZAR = 8
        self.ELIMINAR = 10
        self.BLUE_PORT = 0
        self.GREEN_PORT = 2000
        self.CHUNKSIZE = 1024
        self.hostname = socket.gethostname()
        self.localIP = myIp
        self.contArchivo = 0 #es parte del identificador de archivo 2 bytes
        self.identificadorArchivo = 32 # 1 byte por ser el grupo 1 tenemos un rango de identificador de 32 a 63
        self.idVerde = idV #este se le suma a identificador de archivo
        self.chunksList = []
        self.secureUDPGREEN = secureUDP(self.localIP, self.GREEN_PORT)



    def menu(self):
        opcion = 1
        while opcion != 0:
            print("MENU....")
            print("0. Salir")
            print("1. Depositar Objeto")
            print("2. Obtener Objeto ")
            print("3. Existe Objeto")
            print("4. Esta Completo el Objeto")
            print("5. Localizar Objeto")
            print("6. Eliminar Objeto")
            print("Elija la opcion que desea ejecutar:")
            opcion = int(input())
            if opcion == 1:
                self.depositar()
            elif opcion == 2:
                self.obtener()
            elif opcion == 3:
                self.existe()
            elif opcion == 4:
                self.completo()
            elif opcion == 5:
                self.localizar()
            elif opcion == 6:
                self.eliminar()
            elif opcion == 0:
                sys.exit(0)

#dado un archivo debe dividirlo en tamaños de 1024bytes, añadir encabezado identificadorArchivo/idchunk
#idchunk debe crearse cada vez acá comenzando en 0
    def depositar(self):
        print("Digite la dirección del archivo que desea depositar: ")
        nombreArchivo = input()
        print("Digite IP del Azul con el que desea comunicarse: ")
        direccionIP= input() #Deberia verificarse la direccion con un método de verificar público
        print("Digite puerto de Azul con el que desea comunicarse: ")
        self.BLUE_PORT= int(input())
        identificadorChunk = 0
        archivo = open(nombreArchivo, "r")
        filesize = os.path.getsize(nombreArchivo)
        while filesize > 0:
            if filesize >= self.CHUNKSIZE:
                contenido = archivo.read(self.CHUNKSIZE)
                filesize -= self.CHUNKSIZE
                tipo = (self.DEPOSITAR).to_bytes(1, byteorder="big")
                idArchivo = (self.identificadorArchivo + self.idVerde).to_bytes(1, byteorder="big") + (self.contArchivo).to_bytes(2, byteorder="big")
                idChunk = (identificadorChunk).to_bytes(4, byteorder="big")
                encabezado = tipo + idArchivo + idChunk
                msg = encabezado + contenido.encode('utf-8')
                self.secureUDPGREEN.send(msg, direccionIP, self.BLUE_PORT)
                identificadorChunk += 1
                print(f"{msg}")
            else:
                contenido = archivo.read(filesize)
                filesize -= filesize
                tipo = (self.DEPOSITAR).to_bytes(1, byteorder="big")
                idArchivo = (self.identificadorArchivo + self.idVerde).to_bytes(1, byteorder="big") + (self.contArchivo).to_bytes(2, byteorder="big")
                idChunk = (identificadorChunk).to_bytes(4, byteorder="big")
                encabezado = tipo + idArchivo + idChunk
                msg = encabezado + contenido.encode('utf-8')
                self.secureUDPGREEN.send(msg, direccionIP, self.BLUE_PORT)
                identificadorChunk += 1
                print(f"{msg}")
        identArchivo = int.from_bytes(idArchivo, "big")
        self.chunksList.append(( identArchivo, identificadorChunk))
        self.contArchivo += 1
        return 0

    def obtener(self):#Debe buscar un archivo en el grafo y rearmarlo, dar algún tipo de referencia para el archivo, es como bajar  un archivo del sistema
        pass


    def existe(self):
        pass


    def completo(self):
        print("Digite el ID del archivo que quiere consultar: ")
        idArchivo = input()
        print("Digite IP del Azul con el que desea comunicarse: ")
        direccionIP= input() #Deberia verificarse la direccion con un método de verificar público
        print("Digite puerto de Azul con el que desea comunicarse: ")
        self.BLUE_PORT= int(input())
        tipo = (self.COMPLETO).to_bytes(1, byteorder="big")
        fileID = (idArchivo).to_bytes(2, byteorder="big") #Preguntar a Kathy si el id del archivo es del 32-63 o 32-63+idV
        msg = tipo + fileID
        self.secureUDPGREEN.send(msg, direccionIP, self.BLUE_PORT)
        infoNodo, address = self.secureUDPGREEN.getMessage()


    def localizar(self):
        print("Digite el ID del archivo que quiere consultar: ")
        idArchivo = input()
        print("Digite IP del Azul con el que desea comunicarse: ")
        direccionIP = input()
        print("Digite puerto de Azul con el que desea comunicarse: ")
        self.BLUE_PORT= int(input())
        tipo = (self.COMPLETO).to_bytes(1, byteorder="big")
        fileID = (idArchivo).to_bytes(2, byteorder="big")
        msg = tipo + fileID
        self.secureUDPGREEN.send(msg, direccionIP, self.BLUE_PORT)

    def eliminar(self):
        pass

    def verificarIP(host):
        regex = r"\b(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b"
        x = re.search(regex, host)
        try:
            if host == "localhost":
                print("Verificando direccion.... direccion ip correcta")
            else:
                print("Verificando direccion.... direccion ip correcta")
        except:
            print("Dirección IP Inválida")
            sys.exit(0)

def main():
    print("Ingrese la IP de esta máquina: ")
    myHost = input()
    verificarIP(myHost)
    print("Ingrese el número de verde: ") #id de verde
    idVerde = int(input())
    print("Mi IP es: " + myHost)
    verde = nodoV(myHost, idVerde)
    verde.menu()


if __name__ == '__main__':
	main()
