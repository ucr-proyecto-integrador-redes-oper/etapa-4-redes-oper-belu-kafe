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
            elif opcion == 0:
                sys.exit(0)
        
#dado un archivo debe dividirlo en tamaños de 1024bytes, añadir encabezado identificadorArchivo/idchunk
#idchunk debe crearse cada vez acá comenzando en 0
    def depositar(self):
        print("dijite la direccion del archivo que desea depositar: ")
        nombreArchivo = input()
        print("Dijite ip de Azul con el que desea comunicarse: ")
        direccionIP= input() #Deberia verificarse la direccion con un método de verificar público
        print("Dijite puerto de Azul con el que desea comunicarse: ")
        self.BLUE_PORT= int(input())
        identificadorChunk = 0
        archivo = open(nombreArchivo, "r") 
        filesize = os.path.getsize(nombreArchivo)
        while filesize > 0:
            if filesize >= self.CHUNKSIZE:
                contenido = archivo.read(self.CHUNKSIZE)
                filesize -= self.CHUNKSIZE
                tipo = (self.DEPOSITAR).to_bytes(1, byteorder="big")
                idArchivo = (self.identificadorArchivo +  self.idVerde).to_bytes(1, byteorder="big") + (self.contArchivo).to_bytes(2, byteorder="big")
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
                idArchivo = (self.identificadorArchivo +  self.idVerde).to_bytes(1, byteorder="big") + (self.contArchivo).to_bytes(2, byteorder="big")
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
	
			
def verificarIP(host):
    regex = r"\b(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b"
    x = re.search(regex, host)
    try:
        if host == "localhost":
            print("verificando direccion.... direccion ip correcta")
        else:
            print("verificando direccion.... direccion ip correcta")	
    except:
        print("Dirección IP Invalida")
        sys.exit(0)
	
	

def main():
    print("ingrese la ip de esta máquina: ")
    myHost = input()
    verificarIP(myHost)
    print("Ingrese el numero de verde: ") #id de verde
    idVerde = int(input())
    print("Mi Ip es " + myHost)
    verde = nodoV(myHost, idVerde)
    verde.menu()

    
if __name__ == '__main__':
	main()


