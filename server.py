import socket
import threading

class IRCServer:
    def __init__(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(("127.0.0.1", 8888))
        self.server_socket.listen(5)

        self.clients = []
        self.lock = threading.Lock()

    def start(self):
        print("Server started. Listening for connections...")

        while True:
            client_socket, client_address = self.server_socket.accept()
            client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
            client_thread.start()

    def handle_client(self, client_socket):
        with self.lock:
            self.clients.append(client_socket)

        client_socket.send("Welcome to the IRC server!\n".encode())

        while True:
            try:
                message = client_socket.recv(1024).decode().strip()

                if message == "/quit":
                    self.disconnect_client(client_socket)
                    break

                self.broadcast(message)

            except ConnectionResetError:
                self.disconnect_client(client_socket)
                break

    def disconnect_client(self, client_socket):
        with self.lock:
            self.clients.remove(client_socket)
        client_socket.close()

    def broadcast(self, message):
        with self.lock:
            for client in self.clients:
                client.send(f"{message}\n".encode())

# Start the IRC server
server = IRCServer()
server.start()
