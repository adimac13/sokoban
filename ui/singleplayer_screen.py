from enum import Enum
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QGridLayout, QFileDialog, QMessageBox
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap, QPainter
from engine.board import Board
from pathlib import Path

class State(Enum):
    NORMAL = 1
    DEADLOCK = 2
    WIN = 3

class SinglePlayerScreen(QWidget):
    def __init__(self, parent_window):
        super().__init__()

        self.board = None

        # Creating dict so that it can be later modified
        self.texture_dict = {
            "ground_texture" : QPixmap("./sokoban-assets/environment/ground.png"),
            "box_texture": QPixmap("./sokoban-assets/environment/box.png"),
            "goal_texture" : QPixmap("./sokoban-assets/environment/goal.png"),
            "obstacle_texture" : QPixmap("./sokoban-assets/environment/obstacle.png"),
            "box_on_goal_texture" : QPixmap("./sokoban-assets/environment/box_on_goal.png")
        }

        self.board_size = 600
        self.state = State.NORMAL

        self.parent_window = parent_window
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.text_label = QLabel("")
        self.text_label.setStyleSheet("font-size: 34px; font-weight: bold; color: white; font-family: 'Courier New', monospace;")
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.instruction_label = QLabel(
            "<span style='color: lightgray;'>[W/A/S/D]</span> Move ‎ ‎ •‎ ‎  "
            "<span style='color: lightgray;'>[U]</span> Undo ‎ ‎ •‎ ‎  "
            "<span style='color: lightgray;'>[R]</span> Redo ‎ ‎ •‎ ‎"
            "<span style='color: lightgray;'>[P]</span> Reset ‎ ‎ •‎ ‎"
            "<span style='color: lightgray;'>[M]</span> Solve"
        )
        self.instruction_label.setStyleSheet("font-size: 15px; font-weight: bold; color: gray;")
        self.instruction_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.timer_label = QLabel("")
        self.timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.timer_label.setStyleSheet("font-size: 22px; font-weight: bold; color: white;")

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_display)
        self.elapsed_time = 0

        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(0)
        self.grid_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.stats_label = QLabel("")
        self.stats_label.setStyleSheet("font-size: 18px; font-weight: bold; color: green")
        self.stats_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.deadlock_label = QLabel("")
        self.deadlock_label.setStyleSheet("font-size: 18px; font-weight: bold; color: gray")
        self.deadlock_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Back button
        btn_back = QPushButton("Back to menu")
        btn_back.setFixedSize(150, 40)
        btn_back.clicked.connect(self.back_to_menu)

        # Json Button
        btn_json = QPushButton("Save map")
        btn_json.setFixedSize(150, 40)
        btn_json.clicked.connect(self.get_path)

        # Adding text to layout
        main_layout.addWidget(self.text_label)

        # Adding instruction to layout
        main_layout.addWidget(self.instruction_label)

        # Adding timer to layout
        main_layout.addWidget(self.timer_label)

        # Adding grid to layout
        main_layout.addLayout(self.grid_layout)

        # Adding stats to layout
        main_layout.addWidget(self.stats_label)

        # Adding deadlock label to layout
        main_layout.addWidget(self.deadlock_label)

        # Adding button to save json
        main_layout.addSpacing(20)
        main_layout.addWidget(btn_json, alignment=Qt.AlignmentFlag.AlignCenter)

        # Padding for button
        main_layout.addWidget(btn_back, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(main_layout)

    def get_path(self):
        path = QFileDialog.getExistingDirectory(self, "Choose place to save")
        if path:
            self.board.input_handle('j', path = Path(path))


    def update_display(self):
        self.elapsed_time += 1
        minutes = self.elapsed_time // 60
        seconds = self.elapsed_time % 60
        self.timer_label.setText(f"{minutes:02}:{seconds:02}")

    def setup_board(self, grid_size, num_of_boxes, num_of_obstacles, json_path, selected_player, a_star_move_time, max_a_star_moves):
        self.state = State.NORMAL
        self.text_label.setText("Sokoban")
        self.text_label.setStyleSheet("font-size: 34px; font-weight: bold; color: white; font-family: 'Courier New', monospace;")

        if selected_player == 1:
            self.texture_dict["player_down_texture"] = QPixmap("./sokoban-assets/player/playerJ_down.png")
            self.texture_dict["player_left_texture"] = QPixmap("./sokoban-assets/player/playerJ_left.png")
            self.texture_dict["player_right_texture"] = QPixmap("./sokoban-assets/player/playerJ_right.png")
            self.texture_dict["player_up_texture"] = QPixmap("./sokoban-assets/player/playerJ_up.png")
        else:
            self.texture_dict["player_down_texture"] = QPixmap("./sokoban-assets/player/playerA_down.png")
            self.texture_dict["player_left_texture"] = QPixmap("./sokoban-assets/player/playerA_left.png")
            self.texture_dict["player_right_texture"] = QPixmap("./sokoban-assets/player/playerA_right.png")
            self.texture_dict["player_up_texture"] = QPixmap("./sokoban-assets/player/playerA_up.png")

        self.board = Board(grid_size, num_of_boxes, num_of_obstacles, json_path, a_star_move_time, max_a_star_moves)
        self.grid_size = self.board.get_grid_size()
        self.update_stats()

        self.elapsed_time = 0
        self.timer_label.setText("00:00")
        self.timer.start(1000)

        # Scaling textures for proper viewing
        for texture in self.texture_dict.keys():
            self.texture_dict[texture] = self.texture_dict[texture].scaled(self.board_size // self.grid_size, self.board_size // self.grid_size,
                                                                   Qt.AspectRatioMode.KeepAspectRatio)
        self.draw_board()

    def update_stats(self):
        moves, undo, redo = self.board.get_stats()
        self.stats_label.setText(f'Moves: {moves:03} ‎ ‎ ‎ ‎  <span style="color: lightgreen;">'
                                 f'Undo: {undo}</span> ‎ ‎ ‎ ‎ Redo: {redo}')

        if self.board.evaluation:
            self.deadlock_label.setText("Deadlock: Detected")
        else:
            self.deadlock_label.setText("Deadlock: Not detected")

        # If all boxes are on their positions
        if self.board.status():
            self.state = State.WIN
            self.text_label.setText("Win")
            self.timer.stop()
            self.text_label.setStyleSheet("font-size: 34px; font-weight: bold; color: green; font-family: 'Courier New', monospace;")
        else:
            self.text_label.setText("Sokoban")
            self.text_label.setStyleSheet(
                "font-size: 34px; font-weight: bold; color: white; font-family: 'Courier New', monospace;")


    def draw_board(self, key = None):
        # Cleaning old board
        for i in reversed(range(self.grid_layout.count())):
            widget = self.grid_layout.itemAt(i).widget()
            if widget is not None:
                widget.setParent(None)

        # Creating new board
        player_pos, boxes_pos, goals_pos, obstacles_pos = self.board.get_positions()
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                current_pos = (row, col)

                cell = QLabel()
                cell.setFixedSize(self.board_size // self.grid_size, self.board_size // self.grid_size)
                cell.setStyleSheet("border: 1px solid darkgray;")

                curr_texture = self.texture_dict["ground_texture"]
                combined = curr_texture.copy()
                painter = QPainter(combined)

                if current_pos in boxes_pos and current_pos in goals_pos:
                    painter.drawPixmap(0,0, self.texture_dict["box_on_goal_texture"])
                elif current_pos in boxes_pos:
                    painter.drawPixmap(0, 0, self.texture_dict["box_texture"])
                elif current_pos in goals_pos:
                    painter.drawPixmap(0, 0, self.texture_dict["goal_texture"])
                elif current_pos in obstacles_pos:
                    painter.drawPixmap(0, 0, self.texture_dict["obstacle_texture"])

                if current_pos == player_pos:
                    if key is None or key == 's': painter.drawPixmap(0,0, self.texture_dict["player_down_texture"])
                    elif key == 'w': painter.drawPixmap(0,0, self.texture_dict["player_up_texture"])
                    elif key == 'a': painter.drawPixmap(0,0, self.texture_dict["player_left_texture"])
                    elif key == 'd': painter.drawPixmap(0,0, self.texture_dict["player_right_texture"])

                painter.end()
                cell.setPixmap(combined)


                self.grid_layout.addWidget(cell, row, col)
        self.update_stats()

    def keyPressEvent(self, event):
        if self.state == State.NORMAL:
            if event.key() == Qt.Key.Key_W:
                self.board.input_handle('w', game=True)
                self.draw_board('w')
            elif event.key() == Qt.Key.Key_S:
                self.board.input_handle('s', game=True)
                self.draw_board('s')
            elif event.key() == Qt.Key.Key_A:
                self.board.input_handle('a', game=True)
                self.draw_board('a')
            elif event.key() == Qt.Key.Key_D:
                self.board.input_handle('d', game=True)
                self.draw_board('d')
            elif event.key() == Qt.Key.Key_U:
                bef_pos = self.board.player_pos
                self.board.input_handle('u', game=True)
                curr_pos = self.board.player_pos

                if curr_pos[0] > bef_pos[0]:
                    self.draw_board('w')
                elif curr_pos[0] < bef_pos[0]:
                    self.draw_board('s')
                elif curr_pos[1] > bef_pos[1]:
                    self.draw_board('a')
                elif curr_pos[1] < bef_pos[1]:
                    self.draw_board('d')

            elif event.key() == Qt.Key.Key_R:
                bef_pos = self.board.player_pos
                self.board.input_handle('r', game=True)
                curr_pos = self.board.player_pos

                if curr_pos[0] < bef_pos[0]:
                    self.draw_board('w')
                elif curr_pos[0] > bef_pos[0]:
                    self.draw_board('s')
                elif curr_pos[1] < bef_pos[1]:
                    self.draw_board('a')
                elif curr_pos[1] > bef_pos[1]:
                    self.draw_board('d')

            elif event.key() == Qt.Key.Key_P:
                self.board.input_handle('p', game=True)
                self.elapsed_time = 0
                self.timer_label.setText("00:00")
                self.draw_board()
            elif event.key() == Qt.Key.Key_M:
                self.board.input_handle('m', game=True)

                if not self.board.evaluation:
                    self.board.num_of_moves = 0
                    self.board.num_of_redo = 0
                    self.board.num_of_undo = 0
                    self.final_cmd = self.board.final_cmd
                    if self.final_cmd is not None:
                        self.a_star_solver()
                    else:
                        QMessageBox.warning(self, "Error", "Could not find any route.")
                else:
                    QMessageBox.warning(self, "Error", "Could not find route, because deadlock is detected.")
        elif self.state == State.WIN:
            if event.key() == Qt.Key.Key_P:
                self.board.input_handle('p')
                self.elapsed_time = 0
                self.timer_label.setText("00:00")
                self.timer.start(1000)
                self.state = State.NORMAL
                self.draw_board()

    def a_star_solver(self):
        if self.parent_window.stacked_widget.currentIndex() != 1:
            return
        move = self.final_cmd.pop(0)
        self.board.input_handle(move)
        self.draw_board(move)
        if len(self.final_cmd):
            if self.board.a_star_move_time is not None:
                QTimer.singleShot(self.board.a_star_move_time, self.a_star_solver)
            else:
                QTimer.singleShot(400, self.a_star_solver)
        else:
            pass

    def back_to_menu(self):
        self.timer.stop()
        self.parent_window.stacked_widget.setCurrentIndex(0)
