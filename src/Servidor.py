import random
import socket
import threading
import time
import json
from datetime import datetime


class Servidor:
    def __init__(self):
        self.colores = {
            "VERDE_CLARO": "\033[1;32m",
            "AMARILLO": "\033[1;33m",
            "AZUL_CLARO": "\033[1;34m",
            "MORADO_CLARO": "\033[1;35m",
            "CIAN_CLARO": "\033[1;36m"
        }

        self.ipServer = "192.168.1.108"

        # socket: {ip, nombre, color, hilo} - Formato del diccionario
        self.datos_usuarios = {}
        self.servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.servidor.bind((self.ipServer, 5555))

        # el servidor empieza a esuchar
        self.servidor.listen()

        self.historial = "../public/historial.json"

    def elegir_color(self):
        # función que se encarga de elegir un color aleatorio sin que esté repetido
        colores_disponibles = list(self.colores.values())
        usados = [datos["color"] for datos in self.datos_usuarios.values()]
        disponibles = list(set(colores_disponibles) - set(usados))
        return random.choice(disponibles) if disponibles else random.choice(colores_disponibles)

    def conectar(self):
        while True:
            # acepta la conexión y obtiene los datos
            cliente, direccion = self.servidor.accept()

            # recibe el primer mensaje que contiene el nombre
            nombre = cliente.recv(1024).decode()

            # guarda todos los datos en el diccionario que se relaciona con el socket
            datos = {
                "ip": direccion,
                "nombre": nombre,
                "color": self.elegir_color(),
                "hilo": threading.Thread(target=self.escuchar, args=(cliente,))
            }

            # compara el socket con el diccionario anterior
            self.datos_usuarios[cliente] = datos

            # empieza el hilo de escuchar al cliente, por lo que empieza la envía
            datos["hilo"].start()

            print(f"\r{datos['color']}Se ha conectado {nombre} desde {direccion[0]}\033[0m")  # Muestra que se han
            self.guardar_en_historial("servidor", f"se ha conectado {nombre} desde {direccion[0]}")
            print("> ", end="", flush=True)  # conectado usuarios

    def escuchar(self, cliente):
        # Cada funcion de escuchar se ejecuta en un hilo distinto
        while True:
            try:
                mensaje = cliente.recv(1024).decode()  # Recibe el mensaje
                time.sleep(0.1)

                # Comprueba que el mensaje no sea salir
                if not mensaje or mensaje.split(": ")[-1].strip() == "salir":
                    self.guardar_en_historial(cliente, mensaje)

                    # En caso de que sea salir, desconecta al cliente
                    self.desconectar_cliente(cliente)
                    break

                # Obtiene los datos de los usuarios
                datos = self.datos_usuarios[cliente]

                # Da formato al mensaje para que se muestre del color adecuado
                mensaje_coloreado = f"{datos['color']}{mensaje}\033[0m"

                # Muestra el mensaje con el formato elegido
                self.mostrar_mensaje(mensaje_coloreado)

                # Guarda mensaje sin colorear
                self.guardar_en_historial(cliente, mensaje)

                # Reenvia el mensaje a todos los clientes
                self.reenviar_mensaje(mensaje_coloreado, cliente)

            except:
                # En caso de que haya un error escuchando, se desconecta el cliente
                self.desconectar_cliente(cliente)
                break

    def enviar(self):
        while True:
            # Recoge el mensaje que envía el servidor
            mensaje = input("> ")

            # En caso de que el mensaje sea salir, cierra el servidor completo
            if mensaje == "/cerrar":
                print(f"\n\033[1;31m \n Cerrando servidor... \033[0m")
                self.guardar_en_historial("servidor", mensaje)
                self.guardar_en_historial("servidor", "Cerrando servidor")

                # Envia a todos los clientes que el servidor va a cerrar
                for cliente in list(self.datos_usuarios.keys()):
                    cliente.send("Server: cerrando servidor".encode())

                    # Luego de enviar el mensaje de salir, desconecta los clientes
                    self.desconectar_cliente(cliente, saliendo=True)

                break

            # Si el mensaje es /kick, expulsa al usuario
            elif "/kick" in mensaje:
                self.expulsar(mensaje)

            # Si el mensaje es /users, muestra los usuarios
            elif "/users" == mensaje:
                self.mostrar_usuarios()

            self.guardar_en_historial("servidor", mensaje)

            # Formatea el mensaje
            mensaje_formateado = f"\033[1;36mServidor: {mensaje}\033[0m"

            # Lo reenvía a todos los clientes
            self.reenviar_mensaje(mensaje_formateado, None)

    @staticmethod
    def mostrar_mensaje(mensaje):
        # Da un formato al mensaje para que se vea de una forma legible
        print("\r" + " " * 80, end="")
        print("\r" + mensaje)
        print("> ", end="", flush=True)

    def desconectar_cliente(self, cliente, saliendo=False):
        # Comprueba si el cliente existe
        if cliente not in self.datos_usuarios:
            return

        # En caso de que exista, obtiene los datos
        datos = self.datos_usuarios[cliente]

        # Formato del mensaje
        mensaje = f"\033[1;31m{datos['nombre']} se ha desconectado.\033[0m"

        if not saliendo:
            # Muestra el mensaje de que ha salido del chat
            self.mostrar_mensaje(mensaje)

        # Reenvia el mensaje de que ha salido a todos los clientes
        self.reenviar_mensaje(mensaje, cliente)

        time.sleep(0.1)

        # Elimina el socket de la lista de los clientes conectados
        del self.datos_usuarios[cliente]

        # Cierra la conexión con el socket del cliente
        cliente.close()

    def reenviar_mensaje(self, mensaje, remitente):
        # Recorre todos los sockets conectados
        for cliente in self.datos_usuarios:
            if cliente != remitente:
                try:
                    # No reenvía el mensaje al usuario que lo ha enviado, para que no le salga 2 veces
                    cliente.send(mensaje.encode())  # Envia el mensaje al cliente

                except:
                    # En caso de error, desconecta al cliente para evitar errores
                    self.desconectar_cliente(cliente)

    def ejecutar(self):
        threading.Thread(target=self.conectar, daemon=True).start()
        # El hilo principal es el de enviar información
        self.enviar()

    def mostrar_usuarios(self):
        print(f"CLIENTES CONECTADOS: {len(list(self.datos_usuarios.values()))}")
        print("-------------------------")
        # Recorre todos los clientes para mostrar su nombre y su IP
        for clientes in list(self.datos_usuarios.values()):
            print(f"Nombre: {clientes['nombre']} - IP: {clientes['ip']}")

    def expulsar(self, mensaje):
        try:
            usuario = mensaje.split("/kick ")[1]
            encontrado = False

            # Recorre los clientes para saber su nombre, y así expulsar al usuario
            for cliente, info in list(self.datos_usuarios.items()):
                if info["nombre"] == usuario:
                    self.mostrar_mensaje(f" \033[1;31m Se ha expulsado a {usuario} \033[0m")
                    self.reenviar_mensaje(f"Se ha expulsado a {usuario}", None)
                    # Llama a la función desconectar para echarlo
                    self.desconectar_cliente(cliente, True)
                    encontrado = True  # Para comprobar que el usuario existe

            if not encontrado:
                print("\033[1;31m ERROR - ESE USUARIO NO EXISTE \033[0m")
                self.guardar_en_historial("servidor", "ERROR - ESE USUARIO NO EXISTE")

        except IndexError:
            print(f"\033[1;31m ERROR - El formato del comando es: /kick <nombre_usuario> \033[0m")
            self.guardar_en_historial("servidor", "ERROR - El formato del comando es: /kick <nombre_usuario>")

    def guardar_en_historial(self, cliente, mensaje):
        archivo = self.historial

        if cliente != "servidor":
            datos = self.datos_usuarios.get(cliente)
            if not datos:
                return

            entrada = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "ip": datos["ip"][0],
                "nombre": datos["nombre"],
                "mensaje": mensaje.split(f"{datos['nombre']}: ")[1]
            }

        else:
            entrada = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "ip": self.ipServer,
                "nombre": "Servidor",
                "mensaje": mensaje
            }

        # Añadimos la entrada al archivo
        with open(archivo, "r+", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []

            data.append(entrada)
            f.seek(0)
            json.dump(data, f, indent=4)
            f.truncate()


if __name__ == "__main__":
    Servidor().ejecutar()
