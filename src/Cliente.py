import socket
import threading
import sys


class Cliente:
    def __init__(self, nombre):
        self.nombre = nombre
        self.cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.cliente.connect(("192.168.1.108", 5555))

        # Envia el nombre al servidor
        self.cliente.send(self.nombre.encode())

    def escuchar(self):
        while True:
            try:
                # Recibe el mensaje
                mensaje = self.cliente.recv(1024).decode()
                if mensaje == f"Se ha expulsado a {self.nombre}":
                    # el servidor te ha echado
                    salida = f"\033[1;31m \nTe han expulsado del servidor. \033[0m"
                    self.mostrar_mensaje(salida)
                    self.cliente.close()
                    break

                # Si el mensaje es salir, el usuario se desconecta
                elif mensaje.endswith("cerrando servidor"):
                    self.mostrar_mensaje(f"\n\033[1;31m \n El servidor se ha cerrado \033[0m")
                    self.cliente.close()
                    break

                elif not mensaje:
                    self.mostrar_mensaje(f"\n\033[1;31m \n Saliendo... \033[0m")
                    self.cliente.close()
                    break

                self.mostrar_mensaje(mensaje)

            except:
                # En caso de error, se cierra el socket
                print("\nError de conexión.")
                self.cliente.close()
                break

    @staticmethod
    def mostrar_mensaje(mensaje):
        print("\r" + " " * 80, end="")
        print("\r" + mensaje)
        print("> ", end="", flush=True)

    def enviar(self):
        while True:
            # Recoge el mensaje
            mensaje = input("> ")

            # Si el mensaje del cliente es salir, se desconecta del servidor
            if mensaje.strip().lower() == "/salir":
                # Envia al servidor que se ha desconectado
                self.cliente.send(f"{self.nombre}: salir".encode())
                break

            # Si no, envia la información al servidor
            self.cliente.send(f"{self.nombre}: {mensaje}".encode())

    def ejecutar(self):
        # Ejecuta la función de escuchar en un hilo
        threading.Thread(target=self.enviar, daemon=True).start()

        # El hilo principal es el de enviar información
        self.escuchar()


if __name__ == "__main__":
    nombre = input("Tu nombre: ")
    Cliente(nombre).ejecutar()
