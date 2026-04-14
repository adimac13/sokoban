import json
import threading
from enum import Enum
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QGridLayout, QFileDialog, QMessageBox
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap, QPainter, QColor
from engine.board import Board
from TCP.client import Client
import time

class State(Enum):
    NORMAL = 1
    DEADLOCK = 2
    WIN = 3

name2rgba = {
    0: "255, 255, 0, 150",
    1: "255, 0, 255, 150",
    2: "0, 255, 255, 150",
    3: "255, 0, 0, 150",
    4: "0, 255, 0, 150",
    5: "0, 0, 255, 150",
    6: "120, 199, 106, 150",
    7: "255, 130, 0, 150",
    8: "230, 53, 213, 150",
    9: "227, 68, 215, 150",
}

name2color = {
    0: "yellow",
    1: "purple",
    2: "aqua",
    3: "red",
    4: "green",
    5: "blue",
    6: "light green",
    7: "orange",
    8: "pink",
}

class MultiPlayerScreen(QWidget):
    def __init__(self, parent_window):
        super().__init__()

        self.board = None
        self.client = None
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
            "<span style='color: lightgray;'>[P]</span> Reset"
        )
        self.instruction_label.setStyleSheet("font-size: 15px; font-weight: bold; color: gray;")
        self.instruction_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.player_color_label = QLabel("")
        self.player_color_label.setStyleSheet("font-size: 25px; font-family: 'Courier New', monospace;")
        self.player_color_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

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

        # Adding color label to layout
        main_layout.addWidget(self.player_color_label)

        # Adding grid to layout
        main_layout.addLayout(self.grid_layout)

        # Adding deadlock label to layout
        main_layout.addWidget(self.deadlock_label)

        # Padding for button
        main_layout.addWidget(btn_back, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(main_layout)

    def setup_board(self):
        # Creating TCP client
        self.client_thread = threading.Thread(target=self.handle_client)
        self.client_thread.start()

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

        self.draw_timer = QTimer()
        self.draw_timer.timeout.connect(self.draw_board)
        self.draw_timer.start(100)
        self.player_color_label.setText(f"You are <span style='color: {name2color[self.client_num]};'>{name2color[self.client_num]}</span>")

    def handle_client(self):
        self.client = Client()

    def _update_info(self):
        """
        This function updates crucial info for visualization, using TCP server
        """
        msg_json = self.client.msg
        # print(msg_json)
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
        self._update_info()

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

                    player_pixmap = self.texture_dict["player_down_texture"].copy()

                    # Colouring player, based on the nickname
                    tint_painter = QPainter(player_pixmap)
                    tint_painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceAtop)

                    tint_painter.fillRect(player_pixmap.rect(), QColor(*self._unpack_player_color(current_pos)))
                    # print(self._unpack_player_color(current_pos))
                    # print(name2rgba[self.client_num])

                    tint_painter.end()
                    painter.drawPixmap(0, 0, player_pixmap)
                    # if key is None or key == 's': painter.drawPixmap(0,0, self.texture_dict["player_down_texture"])
                    # elif key == 'w': painter.drawPixmap(0,0, self.texture_dict["player_up_texture"])
                    # elif key == 'a': painter.drawPixmap(0,0, self.texture_dict["player_left_texture"])
                    # elif key == 'd': painter.drawPixmap(0,0, self.texture_dict["player_right_texture"])

                painter.end()
                cell.setPixmap(combined)
                self.grid_layout.addWidget(cell, row, col)

    def _unpack_player_color(self, player_pos):
        nickname = self.players_pos.index(player_pos) + 1 # Adding one, because nicknames start from 1
        color = name2rgba[nickname].split(',')
        final_color = [int(c) for c in color]
        return final_color

    def _key_handle(self, key):
        self.client.message_received.clear()
        self.client.write(key)
        self.client.message_received.wait()

    def keyPressEvent(self, event):
        if self.state == State.NORMAL:
            if event.key() == Qt.Key.Key_W:
                self._key_handle('w')
            elif event.key() == Qt.Key.Key_S:
                self._key_handle('s')
            elif event.key() == Qt.Key.Key_A:
                self._key_handle('a')
            elif event.key() == Qt.Key.Key_D:
                self._key_handle('d')
            elif event.key() == Qt.Key.Key_P:
                pass

        elif self.state == State.WIN:
            if event.key() == Qt.Key.Key_P:
                pass



    def back_to_menu(self):
        self.client.end_of_client = True
        self.client.client.close()
        self.client_thread.join()
        self.draw_timer.stop()
        self.board = None
        self.client = None
        self.players_pos = None
        self.boxes_pos = None
        self.goals_pos = None
        self.obstacles_pos = None
        self.grid_size = None
        self.parent_window.stacked_widget.setCurrentIndex(0)
