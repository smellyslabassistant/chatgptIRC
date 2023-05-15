import socket
import threading
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

class IRCServer:
    def __init__(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(("127.0.0.1", 8888))
        self.server_socket.listen(5)

        self.clients = {}
        self.lock = threading.Lock()

    def start(self):
        print("Server started. Listening for connections...")

        while True:
            client_socket, client_address = self.server_socket.accept()
            client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
            client_thread.start()

    def handle_client(self, client_socket):
        username = self.receive_message(client_socket)
        iv = self.receive_message(client_socket)
        key = self.receive_message(client_socket)

        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())

        with self.lock:
            self.clients[client_socket] = (username, cipher)

        self.send_message(client_socket, "Welcome to the IRC server!\n")

        while True:
            try:
                encrypted_message = self.receive_message(client_socket)
                message = self.decrypt_message(encrypted_message, cipher)

                if message == "/quit":
                    self.disconnect_client(client_socket)
                    break

                self.broadcast_message(message, client_socket)

            except ConnectionResetError:
                self.disconnect_client(client_socket)
                break

    def disconnect_client(self, client_socket):
        with self.lock:
            username, _ = self.clients[client_socket]
            del self.clients[client_socket]
        client_socket.close()
        self.broadcast_message(f"{username} has left the chat.\n", client_socket)

    def broadcast_message(self, message, sender_socket):
        with self.lock:
            sender_username, _ = self.clients[sender_socket]

            for client, (username, cipher) in self.clients.items():
                if client != sender_socket:
                    encrypted_message = self.encrypt_message(f"{sender_username}: {message}", cipher)
                    self.send_message(client, encrypted_message)

    def send_message(self, client_socket, message):
        client_socket.send(message.encode())

    def receive_message(self, client_socket):
        return client_socket.recv(1024).decode().strip()

    def encrypt_message(self, message, cipher):
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(message.encode()) + padder.finalize()
        encryptor = cipher.encryptor()
        encrypted_message = encryptor.update(padded_data) + encryptor.finalize()
        return encrypted_message

    def decrypt_message(self, encrypted_message, cipher):
        decryptor = cipher.decryptor()
        padded_data = decryptor.update(encrypted_message) + decryptor.finalize()
        unpadder = padding.PKCS7(128).unpadder()
        message = unpadder.update(padded_data) + unpadder.finalize()
        return message.decode()

# Start the IRC server
server = IRCServer()
server.start()
