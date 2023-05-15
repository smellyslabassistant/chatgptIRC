import socket
import threading
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

class IRCClient:
    def __init__(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(("127.0.0.1", 8888))

        self.username = input("Enter your username: ")
        self.iv = b'0000000000000000'  # Initialization vector (IV)
        self.key = b'0123456789abcdef'  # Encryption key

        self.cipher = Cipher(algorithms.AES(self.key), modes.CBC(self.iv), backend=default_backend())

        self.send_message(self.username)
        self.send_message(self.iv)
        self.send_message(self.key)

        self.receive_thread = threading.Thread(target=self.receive_messages)
        self.receive_thread.start()

    def receive_messages(self):
        while True:
            try:
                encrypted_message = self.receive_message()
                message = self.decrypt_message(encrypted_message, self.cipher)
                print(message)

            except ConnectionResetError:
                print("Disconnected from the server.")
                self.client_socket.close()
                break

    def send_message(self, message):
        encrypted_message = self.encrypt_message(message, self.cipher)
        self.client_socket.send(encrypted_message)

    def receive_message(self):
        return self.client_socket.recv(1024)

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

    def run(self):
        while True:
            message = input()
            if message == "/quit":
                self.client_socket.close()
                break
            self.send_message(message)

# Start the IRC client
client = IRCClient()
client.run()
