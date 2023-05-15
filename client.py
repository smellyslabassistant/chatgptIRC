import socket
import threading

class IRCClient:
    def __init__(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(("127.0.0.1", 8888))

        self.receive_thread = threading.Thread(target=self.receive_messages)
        self.receive_thread.start()

    def receive_messages(self):
        while True:
            try:
                message = self.client_socket.recv(1024).decode().strip()
                print(message)

            except ConnectionResetError:
                print("Disconnected from the server.")
                self.client_socket.close()
                break

    def send_message(self, message):
        self.client_socket.send(message.encode())

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
