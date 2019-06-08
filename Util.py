import ipaddress
import threading
#import fcntl
import os
import time

DEBUG = False

#Constante para mostrar mensaje de respuestas de los mensajes (Está vivo?...)
SHOW_ANSWERS = True

#Constante para mostrar mensaje que provocan cambios en tabla de enrutamiento
SHOW_CHANGES = False

#Constante para mostrar mensaje de datos que van siendo enrutados
SHOW_DATA_MESSAGE = True

# Constante para mostrar los saltos de los mensajes de inundación
SHOW_FLOOD_HOOPS = True

# Constante para mostrar cuando se ha activado ignorar todos los mensajes
SHOW_IGNORE_MESSAGE_FLAG = True

# Método que pasa una IP de una tupla de enteros a un string
def ip_tuple_to_str(ip_tuple):
    return str(ip_tuple[0]) +"."+str(ip_tuple[1]) +"."+str(ip_tuple[2]) +"."+str(ip_tuple[3])

# Método que para un ip dado por un string a una tupla de enteros
def str_ip_to_tuple(str_ip):
    temp = str_ip.split(".")
    return (int(temp[0]),int(temp[1]),int(temp[2]),int(temp[3]))

# Método que permite traducir un ip a una cadena de 4 bytes
def ip_to_bytes(ip_param):
    result =  ip_param[0].to_bytes(1,"big")
    result += ip_param[1].to_bytes(1,"big")
    result += ip_param[2].to_bytes(1,"big")
    result += ip_param[3].to_bytes(1,"big")
    return result

# Método que permite convertir un ip dado en bytes a una tupla de 4 enteros
def ip_to_int_tuple(bytes_param):
    return (bytes_param[0],bytes_param[1],bytes_param[2],bytes_param[3])    

# Método genérico para la creación de de hilos
def prepare_new_thread(name, pointer_to_method, arguments):
    new_thread = threading.Thread(target=pointer_to_method, args=arguments)
    new_thread.setDaemon(True)
    new_thread.setName(name)
    return new_thread

# Validate an ip address
def valid_addr(address):
    try:
        (ipaddress.ip_address(address))
        return True
    except:
        return False

def valid_port(port):
    return 1024 < port < 2**16

def valid_mask(mask):
    return 2<=mask<=30





# Create a file and write the header
def create_file(filename):
    file = open(filename, 'w')
    file.write("\t\t\t\t\t\t*******************************************************************************\n")
    file.write("\t\t\t\t\t\t************************ " + filename + " ***********************\n")
    file.write("\t\t\t\t\t\t*******************************************************************************\n")
    file.close()


def verifyDirectory(name_directory):
    try:
        os.stat(name_directory)
    except:
        os.mkdir(name_directory)

