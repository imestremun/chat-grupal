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

        self.ipServer = "192.168.100.73"
        self.datos_usuarios = {}  # socket: {ip, nombre, color, hilo} - Formato del diccionario
        self.servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.servidor.bind((self.ipServer, 5555))
        self.servidor.listen()  # el servidor empieza a esuchar

        self.historial = "historial.json"

    def elegir_color(self):  # función que se encarga de elegir un color aleatorio sin que esté repetido
        colores_disponibles = list(self.colores.values())
        usados = [datos["color"] for datos in self.datos_usuarios.values()]
        disponibles = list(set(colores_disponibles) - set(usados))
        return random.choice(disponibles) if disponibles else random.choice(colores_disponibles)

    def conectar(self):
        while True:
            cliente, direccion = self.servidor.accept()  # acepta la conexión y obtiene los datos
            nombre = cliente.recv(1024).decode()  # recibe el primer mensaje que contiene el nombre

            datos = {
                "ip": direccion,
                "nombre": nombre,
                "color": self.elegir_color(),
                "hilo": threading.Thread(target=self.escuchar, args=(cliente,))
            }  # guarda todos los datos en el diccionario que se relaciona con el socket

            self.datos_usuarios[cliente] = datos  # compara el socket con el diccionario anterior
            datos["hilo"].start()  # empieza el hilo de escuchar al cliente, por lo que empieza la envía

            print(f"\r{datos['color']}Se ha conectado {nombre} desde {direccion[0]}\033[0m")  # Muestra que se han
            self.guardar_en_historial("servidor", f"se ha conectado {nombre} desde {direccion[0]}")
            print("> ", end="", flush=True)  # conectado usuarios

    def escuchar(self, cliente):  # Cada funcion de escuchar se ejecuta en un hilo distinto
        while True:
            try:
                mensaje = cliente.recv(1024).decode()  # Recibe el mensaje
                time.sleep(0.1)
                if not mensaje or mensaje.split(": ")[-1].strip() == "salir":  # Comprueba que el mensaje no sea salir
                    self.guardar_en_historial(cliente, mensaje)
                    self.desconectar_cliente(cliente)  # En caso de que sea salir, desconecta al cliente
                    break  # rompe el bucle

                datos = self.datos_usuarios[cliente]  # Obtiene los datos de los usuarios
                # Da formato al mensaje para que se muestre del color adecuado
                mensaje_coloreado = f"{datos['color']}{mensaje}\033[0m"

                self.mostrar_mensaje(mensaje_coloreado)  # Muestra el mensaje con el formato elegido
                self.guardar_en_historial(cliente, mensaje)  # Guarda mensaje sin colorear
                self.reenviar_mensaje(mensaje_coloreado, cliente)  # Reenvia el mensaje a todos los clientes

            except:
                self.desconectar_cliente(cliente)  # En caso de que haya un error escuchando, se desconecta el cliente
                break

    @staticmethod
    def mostrar_mensaje(mensaje):  # Da un formato al mensaje para que se vea de una forma legible
        print("\r" + " " * 80, end="")
        print("\r" + mensaje)
        print("> ", end="", flush=True)

    def desconectar_cliente(self, cliente, saliendo=None):
        if cliente not in self.datos_usuarios:  # Comprueba si el cliente existe
            return
        datos = self.datos_usuarios[cliente]  # En caso de que exista, obtiene los datos

        mensaje = f"\033[1;31m{datos['nombre']} se ha desconectado.\033[0m"  # Formato del mensaje

        if not saliendo:
            self.mostrar_mensaje(mensaje)  # Muestra el mensaje de que ha salido del chat

        self.reenviar_mensaje(mensaje, cliente)  # Reenvia el mensaje de que ha salido a todos los clientes

        time.sleep(0.1)
        del self.datos_usuarios[cliente]  # Elimina el socket de la lista de los clientes conectados
        cliente.close()  # Cierra la conexión con el socket del cliente

    def reenviar_mensaje(self, mensaje, remitente):
        for cliente in self.datos_usuarios:  # Recorre todos los sockets conectados
            if cliente != remitente:  # No reenvía el mensaje al usuario que lo ha enviado, para que no le salga 2 veces
                try:
                    cliente.send(mensaje.encode())  # Envia el mensaje al cliente
                except:
                    self.desconectar_cliente(cliente)  # En caso de error, desconecta al cliente para evitar errores

    def enviar(self):
        while True:
            mensaje = input("> ")  # Recoge el mensaje que envía el servidor
            if mensaje == "/cerrar":  # En caso de que el mensaje sea salir, cierra el servidor completo
                print(f"\n\033[1;31m \n Cerrando servidor... \033[0m")
                self.guardar_en_historial("servidor", mensaje)
                self.guardar_en_historial("servidor", "Cerrando servidor")

                for cliente in list(self.datos_usuarios.keys()):  # Envia a todos los clientes
                    cliente.send("Server: salir".encode())  # que el servidor va a cerrar
                    self.desconectar_cliente(cliente, saliendo=True)  # Luego de enviar el mensaje de salir, desconecta los clientes
                break

            elif "/kick" in mensaje:  # Si el mensaje es /kick, expulsa al usuario
                self.expulsar(mensaje)

            elif "/users" == mensaje:  # Si el mensaje es /users, muestra los usuarios
                self.mostrar_usuarios()

            self.guardar_en_historial("servidor", mensaje)
            mensaje_formateado = f"\033[1;36mServidor: {mensaje}\033[0m"  # Formatea el mensaje
            self.reenviar_mensaje(mensaje_formateado, None)  # Lo reenvía a todos los clientes

    def ejecutar(self):
        threading.Thread(target=self.conectar, daemon=True).start()  # Empieza el hilo para que se conecte el cliente
        self.enviar()  # El hilo principal es el de enviar información

    def mostrar_usuarios(self):
        print(f"CLIENTES CONECTADOS: {len(list(self.datos_usuarios.values()))}")
        print("-------------------------")
        for clientes in list(self.datos_usuarios.values()):  # Recorre todos los clientes para mostrar su nombre y su IP
            print(f"Nombre: {clientes['nombre']} - IP: {clientes['ip']}")

    def expulsar(self, mensaje):
        try:
            usuario = mensaje.split("/kick ")[1]
            encontrado = False
            for cliente, info in list(self.datos_usuarios.items()):  # Recorre los clientes para saber su nombre,
                if info["nombre"] == usuario:  # y así expulsar al usuario

                    self.reenviar_mensaje(f"Se ha expulsado a {usuario}", None)

                    self.desconectar_cliente(cliente)  # Llama a la función desconectar para echarlo
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
