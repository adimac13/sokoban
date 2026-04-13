import threading
import socket
import time
from random import randint
import json

from config import host, port
from engine.board import Board

class Server:
    def __init__(self):
        # Config for sokoban
        self.grid_size = 8
        self.num_of_boxes = 7
        self.num_of_obstacles = 6
        self.players_pos = []

        self.clients = []
        self.nicknames = []
        self.host = host
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.host, self.port))
        self.server.listen()

        self.generate_new_board()

        self.accepting_client() # Endless loop for accepting new clients

    def broadcast(self, message):
        for client in self.clients:
            client.send(message)


    def _key_handle(self, key, client):
        index = self.clients.index(client)
        self.board.player_pos = self.players_pos[index]
        self.board.input_handle(key)
        self.players_pos[index] = self.board.player_pos
        self.send_board_info()

    def handle_client(self, client):
        while True:
            try:
                message = client.recv(1024).decode('ascii')
                if message == "w":
                    self._key_handle('w', client)
                elif message == "s":
                    self._key_handle('s', client)
                elif message == "a":
                    self._key_handle('a', client)
                elif message == "d":
                    self._key_handle('d', client)

            except:
                index = self.clients.index(client)
                self.clients.remove(client)
                client.close()
                nickname = self.nicknames[index]
                self.nicknames.remove(nickname)
                player_pos = self.players_pos[index]
                self.players_pos.remove(player_pos)
                # self.broadcast(f'{nickname} left the chat'.encode('ascii'))
                print(f'Disconnected: {nickname}')
                break

    def accepting_client(self):
        while True:
            client, address = self.server.accept()
            self.clients.append(client)

            # Setting name of the client, with the number of current clients
            client.send(f'NICK'.encode('ascii'))
            _ = client.recv(1024).decode('ascii')
            client.send(f'{len(self.clients)}'.encode('ascii'))
            nickname = len(self.clients)

            # Setting initial position of new client
            client_pos = self.generate_position()
            self.players_pos.append(client_pos)

            print(f'Connected: {address} | {nickname}')
            self.nicknames.append(nickname)
            # client.send(f'Connected'.encode('ascii'))

            thread = threading.Thread(target = self.handle_client, args=(client, ))
            thread.start()

            self.send_board_info()

    def send_board_info(self):
        _, boxes_pos, goals_pos, obstacles_pos = self.board.get_positions()

        data = {
            "player" : self.players_pos,
            "boxes" : boxes_pos,
            "goals" : goals_pos,
            "obstacles" : obstacles_pos,
            "size" : self.grid_size
        }

        data_to_send = json.dumps(data)
        self.broadcast(data_to_send.encode('ascii'))

    def generate_new_board(self):
        self.board = Board(grid_size = self.grid_size, num_of_boxes=self.num_of_boxes, num_of_obstacles=self.num_of_obstacles)

    def generate_position(self):
        _ , boxes_pos, goals_pos, obstacles_pos = self.board.get_positions()
        pos = (randint(0, self.grid_size - 1), randint(0, self.grid_size - 1))

        while pos in boxes_pos or pos in goals_pos or pos in obstacles_pos or pos in self.players_pos:
            pos = (randint(0, self.grid_size - 1), randint(0, self.grid_size - 1))
        return pos


if __name__ == "__main__":
    server = Server()
