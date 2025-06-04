# Chat Grupal con Sockets en Python

Este proyecto implementa un sistema de chat grupal en red utilizando los módulos `socket` y `threading` de Python. Permite a varios clientes conectarse a un servidor central, enviar y recibir mensajes en tiempo real, y cuenta con funciones como historial de mensajes, expulsión de usuarios y cierre seguro del servidor.

---

## Estructura del Proyecto
```
chat/
├── cliente.py # Código del cliente de chat
├── servidor.py # Código del servidor de chat
└── historial.json # Historial de mensajes en formato JSON
```

---

## Requisitos

- Python 3.x
- Red local o configuración de red adecuada para conectar cliente y servidor

---

## Uso

### Ejecutar el Servidor

1. Abre el archivo `servidor.py` y configura la dirección IP local del servidor:
   ```python
    self.ipServer = "192.168.100.73"
   ```

2. Ejecuta el servidor desde la terminal:
   ```bash
   python servidor.py
   ```

El servidor quedará a la espera de conexiones entrantes de clientes.

---

### Ejecutar el Cliente

1. Abre el archivo `cliente.py` y asegúrate de que la IP del servidor esté correctamente configurada.

2. Ejecuta el cliente en una terminal o desde múltiples terminales para simular varios usuarios:
   ```bash
   python cliente.py
   ```

3. Al iniciar, el programa te pedirá que ingreses tu nombre de usuario. A partir de ese momento, podrás enviar mensajes que serán visibles para todos los demás usuarios conectados.

4. Si deseas salir del chat, puedes escribir el comando `/salir`.

---

## Características

### Cliente

- Conexión mediante sockets TCP.
- Entrada interactiva del nombre de usuario.
- Envío de mensajes a través de la terminal.
- Recepción de mensajes en segundo plano mediante `threading`.
- Permite desconexión limpia con el comando `/salir`.

### Servidor

- Acepta múltiples conexiones simultáneas.
- Distribuye todos los mensajes recibidos a todos los clientes activos.
- Asigna un color único a cada usuario para facilitar la lectura de los mensajes.
- Muestra mensajes importantes en consola (conexiones, desconexiones, expulsiones).
- Guarda un historial detallado de los mensajes y eventos en el archivo `historial.json`.
- Soporta comandos administrativos para controlar el servidor y moderar usuarios.

---

## Comandos del Servidor

Mientras el servidor está en ejecución, el administrador puede ingresar los siguientes comandos desde la terminal:

- `/users`  
  Muestra una lista con los nombres de todos los clientes conectados en ese momento.

- `/kick <nombre>`  
  Expulsa del chat al cliente cuyo nombre coincida con el proporcionado.

- `/cerrar`  
  Detiene el servidor de manera segura. Todos los clientes serán notificados de la desconexión y se cerrará la conexión con ellos.

---

## Formato del Historial

Todos los mensajes (incluidos eventos como conexiones, desconexiones, expulsiones y mensajes del servidor) se almacenan en un archivo `historial.json` con el siguiente formato:

```json
[
  {
    "timestamp": "2025-06-04 12:34:56",
    "ip": "192.168.100.100",
    "nombre": "Carlos",
    "mensaje": "Hola a todos"
  }
]
```

Este archivo permite consultar de forma estructurada todo lo que ha ocurrido durante la vida del servidor.

---

## Colores

Cada usuario conectado recibe un color ANSI aleatorio para que sus mensajes se distingan fácilmente en la consola del servidor. Esta funcionalidad mejora la experiencia visual en chats con múltiples usuarios.

---

## Autor

### Iker Mestre - ikermestrem08@gmail.com
