from secureUDP import secureUDP
import sys # Para pasar argumentos
import re # Para usar RegEx (Expresiones Regulares)
import threading

host = ""
port = 0

if len(sys.argv) > 2:
    ip = str(sys.argv[1])
    puerto = str(sys.argv[2])
    regex = r"\b(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b"
    x = re.search(regex, ip)
    try:
        if ip=="localhost":
           host=ip
           port=int(puerto)
        else:
           host=ip
           port=int(puerto)
    except:
        print("Dirección IP Invalida")
        sys.exit(0)
else:
    print("No ingresó argumentos: ")
    print("Debe ingresar ip y puerto en los argumentos")
    sys.exit(0)

secure = secureUDP(ip, int(puerto))


def send():
	while True:
		msj= input()
		oip= input()
		opuerto= input()
		secure.send( msj.encode('utf-8'), oip,int(opuerto))
def recieve():
	while True:
		msj = secure.getMessage()
		print("Mensaje REcibido: " +msj)
	
s = threading.Thread(target=send)
s.start()

r = threading.Thread(target=recieve)
r.start()
