from secureUDP import secureUDP
import sys # Para pasar argumentos
import re # Para usar RegEx (Expresiones Regulares)

host = ""
port = 0

if len(sys.argv) > 2:
    ip = str(sys.argv[1])
    puerto = str(sys.argv[2])
    oip= str(sys.argv[3])
    opuerto = str(sys.argv[4])
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
msj= "Hola"
secure.send( msj.encode('utf-8'), oip,int(opuerto))
secure.getMessage()
