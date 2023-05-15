import socket
from threading import Thread
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from termcolor import colored
import time

KEY = b'Sixteen byte key'  # 16-byte key for AES encryption
PORT = 5001
BUFFER_SIZE = 1024

def encrypt(plain_text):
    cipher = AES.new(KEY, AES.MODE_ECB)
    cipher_text = cipher.encrypt(pad(plain_text.encode(), AES.block_size))
    return cipher_text

def decrypt(cipher_text):
    cipher = AES.new(KEY, AES.MODE_ECB)
    plain_text = unpad(cipher.decrypt(cipher_text), AES.block_size)
    return plain_text.decode()

def receive_messages(client_socket):
    while True:
        cipher_text = client_socket.recv(BUFFER_SIZE)
        message = decrypt(cipher_text)
        if message == "quit":
            client_socket.close()
            break
        else:
            print(colored(message, 'blue'))

def send_messages(client_socket, username):
    while True:
        message = input(">>")
        cipher_text = encrypt(message)
        client_socket.send(cipher_text)
        if message == "/quit":
            time.sleep(.600)
            client_socket.close()
            break

def start_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('localhost', PORT))

    username = input("Enter your username: ")
    client_socket.send(username.encode())

    receive_thread = Thread(target=receive_messages, args=(client_socket,))
    send_thread = Thread(target=send_messages, args=(client_socket, username))

    receive_thread.start()
    send_thread.start()

if __name__ == '__main__':
    start_client()
