import json
import threading
from enum import Enum
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QGridLayout, QFileDialog, QMessageBox
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap, QPainter
from engine.board import Board
from TCP.client import Client
import time

class State(Enum):
    NORMAL = 1
    DEADLOCK = 2
    WIN = 3

class MultiPlayerScreen(QWidget):
    def __init__(self, parent_window):
        super().__init__()

        self.board = None
        self.client = None #TODO client must be set to None when closing the window
        self.players_pos = None
        self.boxes_pos = None
        self.goals_pos = None
        self.obstacles_pos = None
        self.grid_size = None


        # Creating dict so that it can be later modified
        self.texture_dict = {
            "ground_texture" : QPixmap("./sokoban-assets/environment/ground.png"),
            "box_texture": QPixmap("./sokoban-assets/environment/box.png"),
            "goal_texture" : QPixmap("./sokoban-assets/environment/goal.png"),
            "obstacle_texture" : QPixmap("./sokoban-assets/environment/obstacle.png"),
            "box_on_goal_texture" : QPixmap("./sokoban-assets/environment/box_on_goal.png"),
            "player_down_texture_1" : QPixmap("./sokoban-assets/player/playerJ_down.png"),
            "player_left_texture_1" : QPixmap("./sokoban-assets/player/playerJ_left.png"),
            "player_right_texture_1" : QPixmap("./sokoban-assets/player/playerJ_right.png"),
            "player_up_texture_1" : QPixmap("./sokoban-assets/player/playerJ_up.png"),
            "player_down_texture" : QPixmap("./sokoban-assets/player/playerA_down.png"),
            "player_left_texture" : QPixmap("./sokoban-assets/player/playerA_left.png"),
            "player_right_texture" : QPixmap("./sokoban-assets/player/playerA_right.png"),
            "player_up_texture" : QPixmap("./sokoban-assets/player/playerA_up.png")
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
            "<span style='color: lightgray;'>[W/A/S/D]</span> Move ‎ ‎ •‎ ‎ "
            "<span style='color: lightgray;'>[P]</span> Reset ‎ ‎ •‎ ‎"
        )
        self.instruction_label.setStyleSheet("font-size: 15px; font-weight: bold; color: gray;")
        self.instruction_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(0)
        self.grid_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.deadlock_label = QLabel("")
        self.deadlock_label.setStyleSheet("font-size: 18px; font-weight: bold; color: gray")
        self.deadlock_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Back button
        btn_back = QPushButton("Back to menu")
        btn_back.setFixedSize(150, 40)
        btn_back.clicked.connect(self.back_to_menu)

        # Adding text to layout
        main_layout.addWidget(self.text_label)

        # Adding instruction to layout
        main_layout.addWidget(self.instruction_label)

        # Adding grid to layout
        main_layout.addLayout(self.grid_layout)

        # Adding deadlock label to layout
        main_layout.addWidget(self.deadlock_label)

        # Padding for button
        main_layout.addWidget(btn_back, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(main_layout)

    def setup_board(self):
        # Creating TCP client
        client_thread = threading.Thread(target=self.handle_client)
        client_thread.start()

        while self.client is None:
            time.sleep(0.01)

        self.client.nick_received.wait()
        self.client.message_received.wait()

        self._update_info()
        self.client_num = int(self.client.nickname)

        print(self.client_num)

        self.state = State.NORMAL
        self.text_label.setText("Sokoban")
        self.text_label.setStyleSheet("font-size: 34px; font-weight: bold; color: white; font-family: 'Courier New', monospace;")

        # Scaling textures for proper viewing
        for texture in self.texture_dict.keys():
            self.texture_dict[texture] = self.texture_dict[texture].scaled(self.board_size // self.grid_size, self.board_size // self.grid_size,
                                                                   Qt.AspectRatioMode.KeepAspectRatio)
        self.draw_board()

    def handle_client(self):
        self.client = Client()

    def _update_info(self):
        """
        This function updates crucial info for visualization, using TCP server
        """
        msg_json = self.client.msg
        print(msg_json)
        msg_dict = json.loads(msg_json)

        self.players_pos = msg_dict["player"]
        self.boxes_pos = msg_dict["boxes"]
        self.goals_pos = msg_dict["goals"]
        self.obstacles_pos = msg_dict["obstacles"]
        self.grid_size = msg_dict["size"]


    def draw_board(self, key = None):
        # Cleaning old board
        for i in reversed(range(self.grid_layout.count())):
            widget = self.grid_layout.itemAt(i).widget()
            if widget is not None:
                widget.setParent(None)

        # Creating new board
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                current_pos = [row, col]

                cell = QLabel()
                cell.setFixedSize(self.board_size // self.grid_size, self.board_size // self.grid_size)
                cell.setStyleSheet("border: 1px solid darkgray;")

                curr_texture = self.texture_dict["ground_texture"]
                combined = curr_texture.copy()
                painter = QPainter(combined)

                if current_pos in self.boxes_pos and current_pos in self.goals_pos:
                    painter.drawPixmap(0,0, self.texture_dict["box_on_goal_texture"])
                elif current_pos in self.boxes_pos:
                    painter.drawPixmap(0, 0, self.texture_dict["box_texture"])
                elif current_pos in self.goals_pos:
                    painter.drawPixmap(0, 0, self.texture_dict["goal_texture"])
                elif current_pos in self.obstacles_pos:
                    painter.drawPixmap(0, 0, self.texture_dict["obstacle_texture"])

                if current_pos in self.players_pos:
                    if key is None or key == 's': painter.drawPixmap(0,0, self.texture_dict["player_down_texture"])
                    elif key == 'w': painter.drawPixmap(0,0, self.texture_dict["player_up_texture"])
                    elif key == 'a': painter.drawPixmap(0,0, self.texture_dict["player_left_texture"])
                    elif key == 'd': painter.drawPixmap(0,0, self.texture_dict["player_right_texture"])

                painter.end()
                cell.setPixmap(combined)


                self.grid_layout.addWidget(cell, row, col)


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



    def back_to_menu(self):
        self.client.end_of_client = True
        self.client.client.close()
        self.parent_window.stacked_widget.setCurrentIndex(0)
