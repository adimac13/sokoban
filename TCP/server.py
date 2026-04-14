# If you want to host server, run this script
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
        self.grid_size = 7
        self.num_of_boxes = 5
        self.num_of_obstacles = 4
        self.players_pos = []
        self.board_win = False

        self.clients = []
        self.nicknames = []
        self.host = host
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.host, self.port))
        self.server.listen()

        # self.generate_new_board()
        self.board_thread = threading.Thread(target = self.generating_new_board_loop)
        self.board_thread.start()

        self.accepting_client() # Endless loop for accepting new clients

    def broadcast(self, message):
        for client in self.clients:
            client.send(message)

    def generating_new_board_loop(self):
        while True:
            if not len(self.clients):
                self.generate_new_board()
            time.sleep(1)

    def _key_handle(self, key, client):
        index = self.clients.index(client)
        self.board.player_pos = self.players_pos[index]

        # Saving old boxes pos in case, new state collides with player position
        _, boxes_pos, _, _ = self.board.get_positions()
        old_boxes_pos = boxes_pos.copy()

        # Handling standard move
        self.board.input_handle(key)

        # Checking if after move is made, it does not collide with another player
        _, boxes_pos, _, _ = self.board.get_positions()
        new_box_pos = [tuple(pos) for pos in boxes_pos]
        new_player_pos = [tuple(pos) for pos in self.players_pos]
        i = set(new_box_pos) & set(new_player_pos)

        if len(i) > 0:
            # If new move collides with another player pos, old boxes pos are loaded
            self.board.boxes_pos = [tuple(pos) for pos in old_boxes_pos]
        else:
            # Else standard move handling
            self.players_pos[index] = self.board.player_pos

        # Checking whether all boxes are on goal positions
        if self.board.status():
            self.board_win = True

        self.send_board_info()

    def handle_client(self, client):
        while True:
            try:
                message = client.recv(1024).decode('ascii')

                if not self.board_win:
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
                self.send_board_info()
                # self.broadcast(f'{nickname} left the chat'.encode('ascii'))
                print(f'Disconnected: {nickname}')
                break

    def accepting_client(self):
        while True:
            client, address = self.server.accept()
            self.clients.append(client)

            # Setting name of the client, with the number of current clients
            client.send(f'NICK\n'.encode('ascii'))
            _ = client.recv(1024).decode('ascii')

            nickname = 0
            if nickname in self.nicknames:
                while nickname in self.nicknames:
                    nickname += 1

            client.send(f'{nickname}\n'.encode('ascii'))


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
            "size" : self.grid_size,
            "names" : self.nicknames
        }

        data_to_send = json.dumps(data)
        self.broadcast((data_to_send + '\n').encode('ascii'))

    def generate_new_board(self):
        self.board = Board(grid_size = self.grid_size, num_of_boxes=self.num_of_boxes, num_of_obstacles=self.num_of_obstacles)
        self.board_win = False

    def generate_position(self):
        _ , boxes_pos, goals_pos, obstacles_pos = self.board.get_positions()
        pos = (randint(0, self.grid_size - 1), randint(0, self.grid_size - 1))

        while pos in boxes_pos or pos in goals_pos or pos in obstacles_pos or pos in self.players_pos:
            pos = (randint(0, self.grid_size - 1), randint(0, self.grid_size - 1))
        return pos


if __name__ == "__main__":
    server = Server()