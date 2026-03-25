import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget, QWidget, QVBoxLayout, QPushButton, QLabel, QGridLayout
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap
from engine.board import Board
from enum import Enum

class State(Enum):
    NORMAL = 1
    DEADLOCK = 2
    WIN = 3

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sokoban")
        self.setFixedSize(800, 600)
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # Creating two different screens
        self.menu_screen = MenuScreen(self)
        self.game_screen = GameScreen(self)
        self.settings_screen = SettingsScreen(self)

        # 0 -> menu, 1 -> game, 2 -> settings
        self.stacked_widget.addWidget(self.menu_screen)
        self.stacked_widget.addWidget(self.game_screen)
        self.stacked_widget.addWidget(self.settings_screen)


class MenuScreen(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel("Sokoban")
        title.setStyleSheet("font-size: 34px; font-weight: bold")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Buttons
        btn_play = QPushButton("Play")
        btn_settings = QPushButton("Settings")
        btn_exit = QPushButton("Exit")

        for btn in (btn_play, btn_settings, btn_exit):
            btn.setFixedSize(200, 40)

        btn_play.clicked.connect(self.go_to_game)
        btn_settings.clicked.connect(self.go_to_settings)
        btn_exit.clicked.connect(sys.exit)

        # Visuals
        layout.addWidget(title)
        layout.addWidget(btn_play)
        layout.addWidget(btn_settings)
        layout.addWidget(btn_exit)
        self.setLayout(layout)

    def go_to_game(self):
        # Setting idx for 1
        self.parent.game_screen.setup_board(5)
        self.parent.stacked_widget.setCurrentIndex(1)

    def go_to_settings(self):
        # Setting idx for 2
        self.parent.stacked_widget.setCurrentIndex(2)

class GameScreen(QWidget):
    def __init__(self, parent_window):
        super().__init__()

        self.board = None

        # Creating dict so that it can be later modified
        self.texture_dict = {
            "ground_texture" : QPixmap("../sokoban-assets/environment/ground.png"),
            "box_texture" : QPixmap("../sokoban-assets/environment/box.png"),
            "goal_texture" : QPixmap("../sokoban-assets/environment/goal.png"),
            "obstacle_texture" : QPixmap("../sokoban-assets/environment/obstacle.png"),
            "player_down_texture" : QPixmap("../sokoban-assets/player/down.png"),
            "player_left_texture" : QPixmap("../sokoban-assets/player/left.png"),
            "player_right_texture" : QPixmap("../sokoban-assets/player/right.png"),
            "player_up_texture" : QPixmap("../sokoban-assets/player/up.png")
        }

        self.board_size = 300
        self.state = State.NORMAL

        self.parent_window = parent_window
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.text_label = QLabel("")
        self.text_label.setStyleSheet("font-size: 34px; font-weight: bold; color: white")
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(0)
        self.grid_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Back button
        btn_back = QPushButton("Back to menu")
        btn_back.setFixedSize(150, 40)
        btn_back.clicked.connect(self.back_to_menu)

        # Adding text to layout
        main_layout.addWidget(self.text_label)

        # Adding grid to layout
        main_layout.addLayout(self.grid_layout)

        # Padding for button
        main_layout.addSpacing(20)
        main_layout.addWidget(btn_back, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(main_layout)

    def setup_board(self, grid_size):
        self.state = State.NORMAL
        self.text_label.setText("Sokoban")
        self.text_label.setStyleSheet("font-size: 34px; font-weight: bold; color: white")
        for texture in self.texture_dict.keys():
            self.texture_dict[texture] = self.texture_dict[texture].scaled(self.board_size // grid_size, self.board_size // grid_size,
                                                                   Qt.AspectRatioMode.KeepAspectRatio)
        self.grid_size = grid_size
        self.board = Board(grid_size = self.grid_size, json_path = '../engine/saved_boards/board_3.json')
        self.draw_board()

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

                cell.setPixmap(self.texture_dict["ground_texture"])
                if current_pos == player_pos:
                    if key is None or key == 's': cell.setPixmap(self.texture_dict["player_down_texture"])
                    elif key == 'w': cell.setPixmap(self.texture_dict["player_up_texture"])
                    elif key == 'a': cell.setPixmap(self.texture_dict["player_left_texture"])
                    elif key == 'd': cell.setPixmap(self.texture_dict["player_right_texture"])

                elif current_pos in boxes_pos:
                    cell.setPixmap(self.texture_dict["box_texture"])
                elif current_pos in goals_pos:
                    cell.setPixmap(self.texture_dict["goal_texture"])
                elif current_pos in obstacles_pos:
                    cell.setPixmap(self.texture_dict["obstacle_texture"])
                self.grid_layout.addWidget(cell, row, col)

    def keyPressEvent(self, event):
        if self.state == State.NORMAL:
            if event.key() == Qt.Key.Key_W:
                self.board.input_handle('w')
                self.draw_board('w')
            elif event.key() == Qt.Key.Key_S:
                self.board.input_handle('s')
                self.draw_board('s')
            elif event.key() == Qt.Key.Key_A:
                self.board.input_handle('a')
                self.draw_board('a')
            elif event.key() == Qt.Key.Key_D:
                self.board.input_handle('d')
                self.draw_board('d')
            elif event.key() == Qt.Key.Key_U:
                self.board.input_handle('u')
                self.draw_board()
            elif event.key() == Qt.Key.Key_R:
                self.board.input_handle('r')
                self.draw_board()
            elif event.key() == Qt.Key.Key_P:
                self.board.input_handle('p')
                self.draw_board()
            elif event.key() == Qt.Key.Key_M:
                self.board.input_handle('m')
                self.final_cmd = self.board.final_cmd
                self.a_star_solver()

        # If all boxes are on their positions
        if self.board.status():
            self.state = State.WIN
            self.text_label.setText("Win")
            self.text_label.setStyleSheet("font-size: 34px; font-weight: bold; color: green")
        elif self.board.evaluation:
            self.text_label.setText("Deadlock")
            self.text_label.setStyleSheet("font-size: 34px; font-weight: bold; color: red")

    def a_star_solver(self):
        move = self.final_cmd.pop(0)
        self.board.input_handle(move)
        self.draw_board(move)
        if len(self.final_cmd):
            QTimer.singleShot(1000, self.a_star_solver)
        else:
            self.state = State.WIN
            self.text_label.setText("Win")
            self.text_label.setStyleSheet("font-size: 34px; font-weight: bold; color: green")

    def back_to_menu(self):
        self.parent_window.stacked_widget.setCurrentIndex(0)

class SettingsScreen(QWidget):
    def __init__(self, parent_window):
        super().__init__()
        self.parent_window = parent_window

        main_layout = QVBoxLayout()

        self.grid_layout = QGridLayout()

        btn_back = QPushButton("Back to menu")
        btn_back.setFixedSize(150, 40)
        btn_back.clicked.connect(self.back_to_menu)

        main_layout.addLayout(self.grid_layout)
        main_layout.addWidget(btn_back, alignment=Qt.AlignmentFlag.AlignCenter)
        self.setLayout(main_layout)

    def back_to_menu(self):
        self.parent_window.stacked_widget.setCurrentIndex(0)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())