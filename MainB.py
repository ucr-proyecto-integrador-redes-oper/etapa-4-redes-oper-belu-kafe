from clientNode import ClientNode
import sys # Para pasar argumentos
import re # Para usar RegEx (Expresiones Regulares)

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
           print("Dirección IP: ", x.group())
           host=ip
           port=int(puerto)
    except:
        print("Dirección IP Invalida")
        sys.exit(0)
else:
    print("No ingresó argumentos: ")
    print("Debe ingresar ip y puerto en los argumentos")
    sys.exit(0)

blue = ClientNode(host, port)
