import socket
import threading
import sys


class Cliente:
    def __init__(self, nombre):
        self.nombre = nombre
        self.cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.cliente.connect(("192.168.100.73", 5555))
        self.cliente.send(self.nombre.encode())  # Envia el nombre al servidor

    def escuchar(self):
        while True:
            try:
                mensaje = self.cliente.recv(1024).decode()  # Recibe el mensaje
                if mensaje == f"Se ha expulsado a {self.nombre}":
                    salida = f"\033[1;31m \nTe han expulsado del servidor. \033[0m"  # el servidor te ha echado
                    self.mostrar_mensaje(salida)
                    self.cliente.close()
                    sys.exit()

                elif mensaje.endswith("salir") or not mensaje:  # Si el mensaje es salir, el usuario se desconecta
                    print(f"\n\033[1;31m \n El servidor se ha cerrado \033[0m")
                    self.cliente.close()
                    sys.exit()

                self.mostrar_mensaje(mensaje)

            except:
                print("\nError de conexión.")  # En caso de error, se cierra el socket
                self.cliente.close()
                break

    def mostrar_mensaje(self, mensaje):
        print("\r" + " " * 80, end="")  # Da formato al mensaje
        print("\r" + mensaje)

        if mensaje != f"Se ha expulsado a {self.nombre}" or mensaje != "El servidor se ha cerrado":
            print("> ", end="", flush=True)

    def enviar(self):
        while True:
            mensaje = input("> ")  # Recoge el mensaje
            if mensaje.strip().lower() == "/salir":  # Si el mensaje del cliente es salir, se desconecta del servidor
                self.cliente.send(f"{self.nombre}: salir".encode())  # Envia al servidor que se ha desconectado
                break

            self.cliente.send(f"{self.nombre}: {mensaje}".encode())  # Si no, envia la información al servidor

    def ejecutar(self):
        threading.Thread(target=self.escuchar, daemon=True).start()  # Ejecuta la función de escuchar en un hilo
        self.enviar()  # El hilo principal es el de enviar información


if __name__ == "__main__":
    nombre = input("Tu nombre: ")
    Cliente(nombre).ejecutar()
