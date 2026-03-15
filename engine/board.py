from random import randint

class Board:
    def __init__(self, grid_size = 12, num_of_boxes = 3, num_of_obstacles = 3):
        self.grid_size = grid_size
        self.player_pos = [grid_size // 2, grid_size // 2]

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

    def player_move(self, key):
        if key.lower() == 'w':
            new_pos_player = self.player_pos[:]
            new_pos_player[0] -= 1

            # If obstacle or outside the area
            if new_pos_player in self.obstacles_pos or new_pos_player[0] < 0 or new_pos_player[0] >= self.grid_size\
                    or new_pos_player[1] < 0 or new_pos_player[1] >= self.grid_size:
                return

            for i, box in enumerate(self.boxes_pos):
                if new_pos_player == box:
                    new_pos_box = box[:]
                    new_pos_box[0] -= 1

                    if new_pos_box in self.obstacles_pos or new_pos_box in self.boxes_pos or new_pos_box[0] < 0 or new_pos_box[0] >= self.grid_size\
                    or new_pos_box[1] < 0 or new_pos_box[1] >= self.grid_size:
                        return

                    self.boxes_pos[i] = new_pos_box

            self.player_pos = new_pos_player


if __name__ == "__main__":
    b = Board()
    print(b.player_pos, b.boxes_pos, b.goals_pos)