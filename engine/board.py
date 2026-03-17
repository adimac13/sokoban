from random import randint
from collections import deque
from copy import deepcopy

class Board:
    def __init__(self, grid_size = 12, num_of_boxes = 3, num_of_obstacles = 3):
        self.grid_size = grid_size
        self.player_pos = [grid_size // 2, grid_size // 2]
        self.num_of_boxes = num_of_boxes
        self.num_of_obstacles = num_of_obstacles
        self.undo = deque()
        self.redo = deque()

        # Randomly chooses position of boxes
        self.boxes_pos = []
        for i in range(num_of_boxes):
            pos = [randint(1, grid_size - 2), randint(1, grid_size - 2)]
            while pos == self.player_pos or pos in self.boxes_pos:
                pos = [randint(1, grid_size - 2), randint(1, grid_size - 2)]
            self.boxes_pos.append(pos)

        # Randomly chooses positions of goals
        self.goals_pos = []
        for i in range(num_of_boxes):
            pos = [randint(0, grid_size - 1), randint(0, grid_size - 1)]
            while pos == self.player_pos or pos in self.boxes_pos or pos in self.goals_pos:
                pos = [randint(0, grid_size - 1), randint(0, grid_size - 1)]
            self.goals_pos.append(pos)

        # Randomly chooses positions of obstacles
        self.obstacles_pos = []
        for i in range(num_of_obstacles):
            pos = [randint(0, grid_size - 1), randint(0, grid_size - 1)]
            while pos == self.player_pos or pos in self.boxes_pos or pos in self.goals_pos or pos in self.obstacles_pos:
                pos = [randint(0, grid_size - 1), randint(0, grid_size - 1)]
            self.obstacles_pos.append(pos)


    def get_positions(self):
        return self.player_pos, self.boxes_pos, self.goals_pos, self.obstacles_pos

    def input_handle(self, key):
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
        else: return

        old_pos_player = deepcopy(self.player_pos)
        old_pos_boxes = deepcopy(self.boxes_pos)

        new_pos_player = self.player_pos[:]
        new_pos_player [0] += vec[0]
        new_pos_player [1] += vec[1]

        # If obstacle or outside the area
        if new_pos_player in self.obstacles_pos or new_pos_player[0] < 0 or new_pos_player[0] >= self.grid_size\
                or new_pos_player[1] < 0 or new_pos_player[1] >= self.grid_size:
            return

        for i, box in enumerate(self.boxes_pos):
            if new_pos_player == box:
                new_pos_box = box[:]
                new_pos_box [0] += vec[0]
                new_pos_box [1] += vec[1]

                if new_pos_box in self.obstacles_pos or new_pos_box in self.boxes_pos or new_pos_box[0] < 0 or new_pos_box[0] >= self.grid_size\
                or new_pos_box[1] < 0 or new_pos_box[1] >= self.grid_size:
                    return

                self.boxes_pos[i] = new_pos_box
                break

        self.player_pos = new_pos_player

        # If it is movement, clear redo
        self.redo.clear()
        self.undo.append((old_pos_player, old_pos_boxes))

    def _undo_handle(self):
        if self.undo:
            current_pos_player = deepcopy(self.player_pos)
            current_pos_boxes = deepcopy(self.boxes_pos)

            # Getting top element
            top = self.undo.pop()

            self.redo.append((current_pos_player, current_pos_boxes))

            self.player_pos = top[0]
            self.boxes_pos = top[1]


    def _redo_handle(self):
        if self.redo:
            current_pos_player = deepcopy(self.player_pos)
            current_pos_boxes = deepcopy(self.boxes_pos)

            # Getting top element
            top = self.redo.pop()

            self.undo.append((current_pos_player, current_pos_boxes))

            self.player_pos = top[0]
            self.boxes_pos = top[1]



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
    board = Board()

    while True:
        p,b,g,o = board.get_positions()
        draw_board(p,b,g,o,board.grid_size)
        key = input("Press w/a/s/d: ")
        board.input_handle(key)



if __name__ == "__main__":
    sokoban_terminal()