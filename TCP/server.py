import threading
import socket
import time

from config import host, port

class Server:
    def __init__(self):
        self.clients = []
        self.nicknames = []

        self.host = host
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.host, self.port))
        self.server.listen()
        self.accepting_client()

    def broadcast(self, message):
        for client in self.clients:
            client.send(message)


    def handle_client(self, client):
        while True:
            try:
                message = client.recv(1024)
                self.broadcast(message)
            except:
                index = self.clients.index(client)
                self.clients.remove(client)
                client.close()
                nickname = self.nicknames[index]
                self.nicknames.remove(nickname)
                self.broadcast(f'{nickname} left the chat'.encode('ascii'))
                break

    def accepting_client(self):
        while True:
            client, address = self.server.accept()
            self.clients.append(client)

            client.send(f'NICK'.encode('ascii'))
            time.sleep(0.01)
            client.send(f'{len(self.clients)}'.encode('ascii')) # Setting name of the client, with the number of current clients

            nickname = client.recv(1024).decode('ascii')

            print(f'Connected: {address} | {nickname}')
            self.broadcast(f'{nickname} joined the chat\n'.encode('ascii'))
            self.nicknames.append(nickname)
            client.send(f'Connected'.encode('ascii'))

            thread = threading.Thread(target = self.handle_client, args=(client, ))
            thread.start()


if __name__ == "__main__":
    server = Server()
