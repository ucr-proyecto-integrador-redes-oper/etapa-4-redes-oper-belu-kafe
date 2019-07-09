from secureUDP import secureUDP
from Util import str_ip_to_tuple, ip_to_bytes, ip_tuple_to_str, ip_to_int_tuple
import sys
import socket
import csv
from threading import Lock, Thread
from time import sleep
import time
import re # Para usar RegEx (Expresiones Regulares)
import os

import signal
from contextlib import contextmanager

class nodoV():

	# constructor de la clase nodo
    def __init__(self, myIp, idV):  # constructor
        self.DEPOSITAR = 0
        self.EXISTE = 2
        self.REXISTE = 3
        self.COMPLETO = 4
        self.RCOMPLETO = 5
        self.OBTENER = 6 #Get
        self.ROBTENER = 7 #Respuesta Get
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
        self.chunksList = [] #lista de pares que relaciona un archivo con la cantidad de chunks que posee
        self.listaChunkIDs_obtener = [] #Lista de todos los chunkids de un acrhivo para la respuesta de obtener
        self.listaChunkIDs = [] #lista de todos los chunkids de un acrhivo para la respuesta de complete
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
                self.receive()
            elif opcion == 3:
                self.existe()
                self.receive()
                print("Hola existe")
            elif opcion == 4:
                self.completo()
                self.receive()
            elif opcion == 5:
                self.localizar()
                self.receive()
            elif opcion == 6:
                self.eliminar()
                print("El archivo ha sido eliminado correctamentamente...")
            elif opcion == 0:
                sys.exit(0)

#############################################################################
    def timeout(self, time):
        # Register a function to raise a TimeoutError on the signal.
        signal.signal(signal.SIGALRM, self.raise_timeout)
    	# Schedule the signal to be sent after ``time``.
        signal.alarm(time)

        try:
            yield
        except TimeoutError:
            pass
        finally:
            # Unregister the signal so it won't be triggered
        	# if the timeout is not reached.
            signal.signal(signal.SIGALRM, signal.SIG_IGN)

    def raise_timeout(self, signum, frame):
        raise TimeoutError

##############################################################################




    def receive(self): # hilo que se mantiene recibiendo respuestas a solicitudes
        while True:
            with self.timeout(5):
                infoNodo, address = self.secureUDPGREEN.getMessage() # el contenido de infoNodo va a ser diferente dependiendo del tipo de respuesta
                msgId = int(infoNodo[0])
                if int(msgId) == self.RCOMPLETO:
                    chunkNum = int.from_bytes(infoNodo[3:7], "big")
                    id = int.from_bytes(infoNodo[1:3], "big")
                    self.rcompleto(id, chunkNum)
                    self.listaChunkIDs.clear()
                elif int(msgId) == self.REXISTE:
                    idArchivo =  int.from_bytes(infoNodo[1:4], "big")
                    print("Si existe el archivo solicitado con id " + str(idArchivo))
                elif int(msgId) == self.ROBTENER:
                    #LLama a metodo encargado de procesar la respuesta obtenida
                    chunkNum = int.from_bytes(infoNodo[3:7], "big")
                    id = int.from_bytes(infoNodo[1:3], "big")
                    self.robtener(id, chunkNum)
                    self.listaChunkIDs_obtener.clear()
            if infoNodo == 0:
                break

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
                idA = int.from_bytes(idArchivo, "big")
                print("el id de archivo que depositó es " +str(idA))
                idChunk = (identificadorChunk).to_bytes(4, byteorder="big")
                encabezado = tipo + idArchivo + idChunk
                msg = encabezado + contenido.encode('utf-8')
                self.secureUDPGREEN.send(msg, direccionIP, self.BLUE_PORT)
                identificadorChunk += 1
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
        identArchivo = int.from_bytes(idArchivo, "big")
        self.chunksList.append(( identArchivo, identificadorChunk))
        self.contArchivo += 1
        return 0
    def depositar(self):
        print("Digite la dirección del archivo que desea depositar: ")
        nombreArchivo = input()
        print("Digite IP del Azul con el que desea comunicarse: ")
        direccionIP= input() #Deberia verificarse la direccion con un método de verificar público
        print("Digite puerto de Azul con el que desea comunicarse: ")
        self.BLUE_PORT= int(input())

    def obtener(self):#Debe buscar un archivo en el grafo y rearmarlo, dar algún tipo de referencia para el archivo, es como bajar  un archivo del sistema
        print("Digite el ID del archivo que quiere obtener: ")
        idArchivo = input()
        print("Digite IP del Azul con el que desea comunicarse: ")#Azul encargado de hacer bcast entre los demás azules
        direccionIP= input()
        print("Digite puerto de Azul con el que desea comunicarse: ")
        self.BLUE_PORT= int(input())
        tipo = (self.OBTENER).to_bytes(1, byteorder="big")
        fileID = (idArchivo).to_bytes(3, byteorder="big")
        msg = tipo + fileID
        self.secureUDPGREEN.send(msg, direccionIP, self.BLUE_PORT)

    def robtener(self, id, chunkNum):
        self.listaChunkIDs_obtener.append(chunkNum) 
        self.listaChunkIDs_obtener = list(dict.fromkeys(self.listaChunkIDs_obtener)) # elimina duplicados de la lista
        




    def existe(self):
        print("Digite el ID del archivo que quiere consultar: ")
        idArchivo = input()
        print("Digite IP del Azul con el que desea comunicarse: ")
        direccionIP= input() #Deberia verificarse la direccion con un método de verificar público
        print("Digite puerto de Azul con el que desea comunicarse: ")
        self.BLUE_PORT= int(input())
        msg =(self.EXISTE).to_bytes(1, byteorder="big") + (idArchivo).to_bytes(3, byteorder="big")


    def completo(self):
        print("Digite el ID del archivo que quiere consultar: ")
        idArchivo = input()
        print("Digite IP del Azul con el que desea comunicarse: ")
        direccionIP= input() #Deberia verificarse la direccion con un método de verificar público
        print("Digite puerto de Azul con el que desea comunicarse: ")
        self.BLUE_PORT= int(input())

        tipo = (self.COMPLETO).to_bytes(1, byteorder="big")
        fileID = (idArchivo).to_bytes(3, byteorder="big") #Preguntar a Kathy si el id del archivo es del 32-63 o 32-63+idV
        msg = tipo + fileID
        self.secureUDPGREEN.send(msg, direccionIP, self.BLUE_PORT)

    def rcompleto(self, id, chunkNum):
        self.listaChunkIDs.append(chunkNum)
        self.listaChunkIDs = list(dict.fromkeys(self.listaChunkIDs)) # elimina duplicados de la lista
        size = 0
        for x, y in self.chunkList: # busca la cantidad de chunks que debería de tener un archivo
            if (x == id):
                size = y
                break

        if (len(self.listaChunkIDs)-1 == size):
            print("Archivo Completo!")
            return True
        else:
            print("Archivo Corrupto")
            return False

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
        print("Digite el ID del archivo que desea eLiminar: ")
        idArchivo = input()
        print("Digite IP del Azul con el que desea comunicarse: ")
        direccionIP= input() #Deberia verificarse la direccion con un método de verificar público
        print("Digite puerto de Azul con el que desea comunicarse: ")
        self.BLUE_PORT= int(input())
        msg =(self.ELIMINAR).to_bytes(1, byteorder="big") + (idArchivo).to_bytes(3, byteorder="big")

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
