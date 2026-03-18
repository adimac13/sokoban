from random import randint
from collections import deque
import json
from pathlib import Path

class Board:
    def __init__(self, grid_size = 12, num_of_boxes = 3, num_of_obstacles = 3, json_path = None):
        self.undo = deque()
        self.redo = deque()
        self.num_of_moves = 0
        self.num_of_undo = 0
        self.num_of_redo = 0

        if json_path is None:
            self.grid_size = grid_size
            self.player_pos = (grid_size // 2, grid_size // 2)
            self.num_of_boxes = num_of_boxes
            self.num_of_obstacles = num_of_obstacles

            # Randomly chooses position of boxes
            self.boxes_pos = []
            for i in range(num_of_boxes):
                pos = (randint(1, grid_size - 2), randint(1, grid_size - 2))
                while pos == self.player_pos or pos in self.boxes_pos:
                    pos = (randint(1, grid_size - 2), randint(1, grid_size - 2))
                self.boxes_pos.append(pos)

            # Randomly chooses positions of goals
            self.goals_pos = []
            for i in range(num_of_boxes):
                pos = (randint(0, grid_size - 1), randint(0, grid_size - 1))
                while pos == self.player_pos or pos in self.boxes_pos or pos in self.goals_pos:
                    pos = (randint(0, grid_size - 1), randint(0, grid_size - 1))
                self.goals_pos.append(pos)

            # Randomly chooses positions of obstacles
            self.obstacles_pos = []
            for i in range(num_of_obstacles):
                pos = (randint(0, grid_size - 1), randint(0, grid_size - 1))
                while pos == self.player_pos or pos in self.boxes_pos or pos in self.goals_pos or pos in self.obstacles_pos:
                    pos = (randint(0, grid_size - 1), randint(0, grid_size - 1))
                self.obstacles_pos.append(pos)
        else:
            with open(str(json_path), 'r') as f:
                self.boxes_pos = []
                self.goals_pos = []
                self.obstacles_pos = []

                data = json.load(f)

                p = data['player']
                b = data['boxes']
                g = data['goals']
                o = data['obstacles']
                s = data['size']

                self.player_pos = tuple(p)

                for box in b:
                    self.boxes_pos.append(tuple(box))

                for goal in g:
                    self.goals_pos.append(tuple(goal))

                for obstacle in o:
                    self.obstacles_pos.append(tuple(obstacle))

                self.grid_size = s

        # Saving initial position for reset
        self.initial_pos = [self.player_pos, self.boxes_pos.copy()]


    def get_positions(self):
        return self.player_pos, self.boxes_pos, self.goals_pos, self.obstacles_pos

    def get_stats(self):
        return self.num_of_moves, self.num_of_undo, self.num_of_redo

    def input_handle(self, key, path = Path('./')):
        if key.lower() == 'w': vec = [-1, 0]    # going up
        elif key.lower() == 's': vec = [1, 0]   # going down
        elif key.lower() == 'a': vec = [0, -1]  # going left
        elif key.lower() == 'd': vec = [0, 1]   # going right
        elif key.lower() == 'u':
            self._undo_handle()
            return
        elif key.lower() == 'r':
            self._redo_handle()
            return
        elif key.lower() == 'p':
            self._reset_handle()
            return
        elif key.lower() == 'j':
            self._save_to_json(path)
            return
        else: return

        old_pos_player = self.player_pos
        old_pos_boxes = self.boxes_pos.copy()

        new_pos_player = (self.player_pos[0] + vec[0], self.player_pos[1] + vec[1])

        # If obstacle or outside the area
        if new_pos_player in self.obstacles_pos or new_pos_player[0] < 0 or new_pos_player[0] >= self.grid_size\
                or new_pos_player[1] < 0 or new_pos_player[1] >= self.grid_size:
            return

        for i, box in enumerate(self.boxes_pos):
            if new_pos_player == box:
                new_pos_box = (box[0] + vec[0], box[1] + vec[1])

                if new_pos_box in self.obstacles_pos or new_pos_box in self.boxes_pos or new_pos_box[0] < 0 or new_pos_box[0] >= self.grid_size\
                or new_pos_box[1] < 0 or new_pos_box[1] >= self.grid_size:
                    return

                self.boxes_pos[i] = new_pos_box
                break

        self.player_pos = new_pos_player
        self.num_of_moves += 1

        # If it is movement, clear redo
        self.redo.clear()
        self.undo.append((old_pos_player, old_pos_boxes))

    def _undo_handle(self):
        if self.undo:
            current_pos_player = self.player_pos
            current_pos_boxes = self.boxes_pos.copy()

            # Getting top element
            top = self.undo.pop()

            self.redo.append((current_pos_player, current_pos_boxes))

            self.player_pos = top[0]
            self.boxes_pos = top[1]
            self.num_of_undo += 1


    def _redo_handle(self):
        if self.redo:
            current_pos_player = self.player_pos
            current_pos_boxes = self.boxes_pos.copy()

            # Getting top element
            top = self.redo.pop()

            self.undo.append((current_pos_player, current_pos_boxes))

            self.player_pos = top[0]
            self.boxes_pos = top[1]
            self.num_of_redo += 1

    def _reset_handle(self):
        self.redo.clear()
        self.undo.clear()
        self.boxes_pos.clear()
        self.player_pos = self.initial_pos[0]
        self.boxes_pos = self.initial_pos[1].copy()
        self.num_of_moves = 0
        self.num_of_redo = 0
        self.num_of_undo = 0

    def _save_to_json(self, path):
        f = {
            "player" : self.player_pos,
            "boxes" : self.boxes_pos,
            "goals" : self.goals_pos,
            "obstacles" : self.obstacles_pos,
            "size" : self.grid_size
        }
        f_str = json.dumps(f)

        saving_path = path / 'sample.json'
        with open(str(saving_path), "w") as f:
            f.write(f_str)

    def status(self):
        i = set(self.boxes_pos) & set(self.goals_pos)
        if len(i) == len(self.goals_pos):
            return 1
        return 0


def draw_board(player, boxes, goals, obstacles, size):
    import os
    grid = [['.' for i in range(size)] for j in range(size)]

    for goal in goals:
        grid[goal[0]][goal[1]] = 'G'

    grid [player[0]][player[1]] = 'P'

    for box in boxes:
        grid[box[0]][box[1]] = 'B'

    for obstacle in obstacles:
        grid[obstacle[0]][obstacle[1]] = 'O'

    os.system('cls' if os.name == 'nt' else 'clear')
    for row in grid:
        print(" ".join(row))

def sokoban_terminal():
    board = Board(json_path='sample.json')

    while True:
        p,b,g,o = board.get_positions()
        draw_board(p,b,g,o,board.grid_size)
        if board.status():
            print("Won")
            break
        else:
            key = input("Press w/a/s/d: ")
            board.input_handle(key)



if __name__ == "__main__":
    sokoban_terminal()