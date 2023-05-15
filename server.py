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

def client_handler(client_socket, client_address, clients, usernames):
    username = client_socket.recv(BUFFER_SIZE).decode()
    print(colored(f"[*] New connection from {client_address[0]}: {username}", 'green'))
    clients.append(client_socket)
    usernames[client_socket] = username

    while True:
        try:
            cipher_text = client_socket.recv(BUFFER_SIZE)
            message = decrypt(cipher_text)
            if message == "/quit":
                client_socket.send(encrypt("quitting."))
                time.sleep(.200)
                client_socket.send(encrypt("quitting.."))
                time.sleep(.200)
                client_socket.send(encrypt("quitting..."))
                client_socket.close()
                clients.remove(client_socket)
                del usernames[client_socket]
                print(colored(f"[-] Disconnected: {username}", 'red'))
                break
            else:
                print(colored(f"{username}: {message}", 'blue'))
                for client in clients:
                    if client != client_socket:
                        client.send(encrypt(f"{username}: {message}"))
        except:
            client_socket.close()
            clients.remove(client_socket)
            del usernames[client_socket]
            print(colored(f"[-] Disconnected: {username}", 'red'))
            break

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', PORT))
    server_socket.listen(5)
    print(colored("[+] Server started!", 'green'))

    clients = []
    usernames = {}
    while True:
        client_socket, client_address = server_socket.accept()
        thread = Thread(target=client_handler, args=(client_socket, client_address, clients, usernames))
        thread.start()

if __name__ == '__main__':
    start_server()
