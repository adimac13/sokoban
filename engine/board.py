from random import randint
from collections import deque
import json
from pathlib import Path
from .evaluation import find_deadlocks, heuristic_evaluation, evaluate_board
from itertools import permutations
from .a_star_algorithm import find_shortest_path
import time

class Board:
    def __init__(self, grid_size = 6, num_of_boxes = 3, num_of_obstacles = 3, json_path = None, a_star_move_time = None, max_a_star_moves = None):
        self.ai_pos = None
        self.box_moved = False # Flag whether box was moved, it is only used for ai mode
        self.undo = deque()
        self.redo = deque()
        self.num_of_moves = 0
        self.num_of_undo = 0
        self.num_of_redo = 0
        self.final_cmd = None
        self.a_star_move_time = a_star_move_time
        self.max_a_star_moves = max_a_star_moves

        # Setting all permutations at the beginning for faster heuristic evaluation
        self.all_permutations = list(permutations(range(num_of_boxes)))

        if json_path is None:
            self.grid_size = grid_size
            self.player_pos = (grid_size // 2, grid_size // 2)
            self.num_of_boxes = num_of_boxes
            self.num_of_obstacles = num_of_obstacles

            self.evaluation = 1
            # Randomly chooses position of boxes
            while self.evaluation:
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
                self.evaluation = evaluate_board(self.boxes_pos, self.obstacles_pos, self.goals_pos, self.grid_size)
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
        self.evaluation = evaluate_board(self.boxes_pos, self.obstacles_pos, self.goals_pos, self.grid_size)

    def find_random_free_space(self):
        pos = (randint(0, self.grid_size - 1), randint(0, self.grid_size - 1))
        while pos == self.player_pos or pos in self.boxes_pos or pos in self.goals_pos or pos in self.obstacles_pos:
            pos = (randint(0, self.grid_size - 1), randint(0, self.grid_size - 1))
        return pos

    def get_positions(self):
        return self.player_pos, self.boxes_pos, self.goals_pos, self.obstacles_pos

    def get_stats(self):
        return self.num_of_moves, self.num_of_undo, self.num_of_redo

    def input_handle(self, key, path = Path('./'), game = False, ai = False):
        if key.lower() == 'w': vec = [-1, 0]    # going up
        elif key.lower() == 's': vec = [1, 0]   # going down
        elif key.lower() == 'a': vec = [0, -1]  # going left
        elif key.lower() == 'd': vec = [0, 1]   # going right
        elif key.lower() == 'u':
            self._undo_handle()
            self.evaluation = evaluate_board(self.boxes_pos, self.obstacles_pos, self.goals_pos, self.grid_size)
            return
        elif key.lower() == 'r':
            self._redo_handle()
            self.evaluation = evaluate_board(self.boxes_pos, self.obstacles_pos, self.goals_pos, self.grid_size)
            return
        elif key.lower() == 'p':
            self._reset_handle()
            return
        elif key.lower() == 'j':
            self._save_to_json(path)
            return
        elif key.lower() == 'm':
            if not ai:
                self.final_cmd = self._optimal_path()
            else:
                self.final_cmd = self._ai_optimal_path()
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

                # Evaluation
                other_boxes_pos = [box for j,box in enumerate(self.boxes_pos) if j!=i]

                if not game:
                    self.evaluation = find_deadlocks(new_pos_box, other_boxes_pos, self.obstacles_pos, self.goals_pos, self.grid_size)
                else:
                    self.evaluation = evaluate_board(self.boxes_pos, self.obstacles_pos, self.goals_pos, self.grid_size)

                break

        if not ai:
            self.box_moved = True

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
            self.num_of_moves -= 1


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
            self.num_of_moves += 1

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
        data = {
            "player" : self.player_pos,
            "boxes" : self.boxes_pos,
            "goals" : self.goals_pos,
            "obstacles" : self.obstacles_pos,
            "size" : self.grid_size
        }

        path.mkdir(exist_ok=True, parents=True)

        num_of_files = len(list(path.glob('*board*')))
        saving_path = path / f'board_{num_of_files}.json'
        with open(str(saving_path), "w") as f:
            json.dump(data, f)

    def _optimal_path(self):
        return find_shortest_path(self.player_pos, self.boxes_pos, self.goals_pos, self.obstacles_pos, self.grid_size, self.max_a_star_moves)

    def _ai_optimal_path(self):
        return find_shortest_path(self.ai_pos, self.boxes_pos, self.goals_pos, self.obstacles_pos, self.grid_size, self.max_a_star_moves, ai = True)

    def status(self):
        # 1 if all boxes are on goal positions, else 0
        i = set(self.boxes_pos) & set(self.goals_pos)
        if len(i) == len(self.goals_pos):
            return 1
        return 0

    def min_number_of_moves(self):
        return heuristic_evaluation(self.player_pos, self.boxes_pos, self.goals_pos)

    def get_grid_size(self):
        return self.grid_size

# ------------------- TERMINAL HANDLE ---------------------

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
    # board = Board(json_path='./saved_boards/board_1.json')
    board = Board()

    while True:
        p,b,g,o = board.get_positions()
        draw_board(p,b,g,o,board.grid_size)
        if board.status():
            print("Won")
            break
        else:
            print(board.min_number_of_moves())
            print(board.evaluation)
            key = input("Press w/a/s/d: ")
            board.input_handle(key)

            if key.lower() == 'm':
                final_cmd = board.final_cmd

                for cmd in final_cmd:
                    p, b, g, o = board.get_positions()
                    draw_board(p, b, g, o, board.grid_size)
                    board.input_handle(cmd)
                    time.sleep(1)

                p, b, g, o = board.get_positions()
                draw_board(p, b, g, o, board.grid_size)

                break



if __name__ == "__main__":
    sokoban_terminal()