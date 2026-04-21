import time
from enum import Enum
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QGridLayout, QHBoxLayout
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap, QPainter, QFont
from engine.board import Board
from threading import Thread
import threading

class State(Enum):
    NORMAL = 1
    DEADLOCK = 2
    WIN = 3

class AIScreen(QWidget):
    def __init__(self, parent_window):
        super().__init__()

        self.board = None
        self.game_lock = threading.Lock()
        self.move_made = False # States whether move was made, so ai can change approach
        self.ai_move_time = 1

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
            "<span style='color: lightgray;'>[W/A/S/D]</span> Move "
        )
        self.instruction_label.setStyleSheet("font-size: 15px; font-weight: bold; color: gray;")
        self.instruction_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(0)
        self.grid_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.ai_status = QLabel("")
        self.ai_status.setStyleSheet("font-size: 21px; font-weight: bold; color: lightgreen")
        self.ai_status.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Button to choose normal ai mode
        self.btn_normal = QPushButton("Normal")
        self.btn_normal.setFixedSize(90, 40)
        self.btn_normal.setFont(QFont('font-family: Courier New', 12))
        self.btn_normal.clicked.connect(self.normal_mode)

        # Button to choose aggressive ai mode
        self.btn_aggressive = QPushButton("Aggressive")
        self.btn_aggressive.setFixedSize(90, 40)
        self.btn_aggressive.setFont(QFont('font-family: Courier New', 12))
        self.btn_aggressive.clicked.connect(self.aggressive_mode)

        # Back button
        btn_back = QPushButton("Back to menu")
        btn_back.setFixedSize(150, 40)
        btn_back.clicked.connect(self.back_to_menu)

        # Adding text to layout
        main_layout.addWidget(self.text_label)

        # Adding instruction to layout
        main_layout.addWidget(self.instruction_label)

        # Adding layout for mode choosing
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(self.btn_aggressive)
        mode_layout.addWidget(self.btn_normal)
        main_layout.addLayout(mode_layout)

        # Adding grid to layout
        main_layout.addLayout(self.grid_layout)

        # Adding deadlock label to layout
        main_layout.addWidget(self.ai_status)

        # Padding for button
        main_layout.addWidget(btn_back, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(main_layout)

    def setup_board(self, grid_size, num_of_boxes, num_of_obstacles, json_path, selected_player, a_star_move_time, max_a_star_moves):
        self.state = State.NORMAL
        self.text_label.setText("Sokoban")
        self.text_label.setStyleSheet("font-size: 34px; font-weight: bold; color: white; font-family: 'Courier New', monospace;")

        self.texture_dict["player_down_texture"] = QPixmap("./sokoban-assets/player/playerJ_down.png")
        self.texture_dict["ai_down_texture"] = QPixmap("./sokoban-assets/player/playerA_down.png")

        self.board = Board(grid_size = 6)
        self.grid_size = self.board.get_grid_size()
        self.update_stats()

        # Scaling textures for proper viewing
        for texture in self.texture_dict.keys():
            self.texture_dict[texture] = self.texture_dict[texture].scaled(self.board_size // self.grid_size, self.board_size // self.grid_size,
                                                                   Qt.AspectRatioMode.KeepAspectRatio)
        self.draw_timer = QTimer()
        self.draw_timer.timeout.connect(self.draw_board)
        self.draw_timer.start(50)

        # ai_pos can be only modified in ai_thread
        self.btn_normal.setStyleSheet("background-color: #447387;")
        self.btn_aggressive.setStyleSheet("")
        self.ai_move_time = 1
        self.move_made = False
        self.ai_flag = False
        self.ai_pos = self.board.find_random_free_space()
        self.board.ai_pos = self.ai_pos
        self.ai_thread = Thread(target=self.ai_handle)
        self.ai_thread.start()

    def normal_mode(self):
        self.ai_move_time = 1
        self.btn_normal.setStyleSheet("background-color: #447387;")
        self.btn_aggressive.setStyleSheet("")

    def aggressive_mode(self):
        self.ai_move_time = 0.2
        self.btn_aggressive.setStyleSheet("background-color: #447387;")
        self.btn_normal.setStyleSheet("")


    def ai_handle(self):
        self.ai_status.setText("AI status: Thinking...")
        time.sleep(1)
        while self.parent_window.stacked_widget.currentIndex() == 4 and self.state != State.WIN:
            self.ai_status.setText("AI status: Thinking...")
            time.sleep(1)

            with self.game_lock:
                self.board.ai_pos = self.ai_pos
                self.board.input_handle('m', game=True, ai = True)

            if not self.board.evaluation:
                if self.board.final_cmd is not None:
                    # self.a_star_solver()
                    self.ai_status.setText("AI status: Working")
                    while len(self.board.final_cmd) and self.parent_window.stacked_widget.currentIndex() == 4 and not self.board.box_moved:
                        self._ai_move()
                        time.sleep(self.ai_move_time)
                    if self.board.box_moved:
                        self.board.final_cmd = []
                        with self.game_lock:
                            self.board.box_moved = False

                else:
                    self.ai_status.setText("AI status: Can't find any route")
                    break
            else:
                self.ai_status.setText("AI status: Can't find any route because of deadlock")
                break

        if self.state == State.WIN:
            self.ai_status.setText("AI status: Stopped")

    def _ai_move(self):
        print(len(self.board.final_cmd))
        if self.parent_window.stacked_widget.currentIndex() != 4:
            return

        with self.game_lock:
            move = self.board.final_cmd.pop(0)

            cur_pos = self.board.player_pos
            self.board.player_pos = self.ai_pos

            self.board.input_handle(move, ai = True)

            self.ai_pos = self.board.player_pos
            self.board.player_pos = cur_pos

    def update_stats(self):
        # If all boxes are on their positions
        if self.board.status():
            self.state = State.WIN
            self.text_label.setText("Win")
            self.text_label.setStyleSheet("font-size: 34px; font-weight: bold; color: green; font-family: 'Courier New', monospace;")
        else:
            self.text_label.setText("Sokoban")
            self.text_label.setStyleSheet(
                "font-size: 34px; font-weight: bold; color: white; font-family: 'Courier New', monospace;")


    def draw_board(self, key = None):
        with self.game_lock:
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
                        painter.drawPixmap(0,0, self.texture_dict["player_down_texture"])

                    if current_pos == self.ai_pos:
                        painter.drawPixmap(0, 0, self.texture_dict["ai_down_texture"])

                    painter.end()
                    cell.setPixmap(combined)

                    self.grid_layout.addWidget(cell, row, col)
            self.update_stats()

    def _wait_for_ai(self):
        while self.ai_flag:
            time.sleep(0.1)

    def keyPressEvent(self, event):
        if self.state == State.NORMAL:
            with self.game_lock:
                if event.key() == Qt.Key.Key_W:
                    self.board.input_handle('w', game=True)
                    self.move_made = True
                elif event.key() == Qt.Key.Key_S:
                    self.board.input_handle('s', game=True)
                    self.move_made = True
                elif event.key() == Qt.Key.Key_A:
                    self.board.input_handle('a', game=True)
                    self.move_made = True
                elif event.key() == Qt.Key.Key_D:
                    self.board.input_handle('d', game=True)
                    self.move_made = True
                elif event.key() == Qt.Key.Key_U:
                    pass
                    # self.board.input_handle('u', game=True)

                elif event.key() == Qt.Key.Key_R:
                    # self.board.input_handle('r', game=True)
                    pass

                elif event.key() == Qt.Key.Key_P:
                    pass

        elif self.state == State.WIN:
            if event.key() == Qt.Key.Key_P:
                self.board.input_handle('p')
                self.state = State.NORMAL

    def back_to_menu(self):
        self.draw_timer.stop()
        self.parent_window.stacked_widget.setCurrentIndex(0)
