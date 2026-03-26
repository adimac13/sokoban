import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget, QWidget, QVBoxLayout, QPushButton, QLabel, \
    QGridLayout, QFileDialog, QMessageBox, QSlider, QFrame, QHBoxLayout
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap, QPainter
from engine.board import Board
from enum import Enum
from pathlib import Path
from copy import copy

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

        self.grid_size = self.settings_screen.grid_size_final

        # 0 -> menu, 1 -> game, 2 -> settings
        self.stacked_widget.addWidget(self.menu_screen)
        self.stacked_widget.addWidget(self.game_screen)
        self.stacked_widget.addWidget(self.settings_screen)

        # Creating game settings
        self.grid_size = 8
        self.num_of_boxes = 4
        self.num_of_obstacles = 4
        self.json_path = None


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
        btn_exit = QPushButton("Exit")
        btn_settings = QPushButton("Settings")

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
        self.parent.game_screen.setup_board(self.parent.settings_screen.grid_size_final, self.parent.settings_screen.num_of_boxes_final,
                                            self.parent.settings_screen.num_of_obstacles_final, self.parent.settings_screen.selected_json_path_final)

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

    def setup_board(self, grid_size, num_of_boxes, num_of_obstacles, json_path):
        self.state = State.NORMAL
        self.text_label.setText("Sokoban")
        self.text_label.setStyleSheet("font-size: 34px; font-weight: bold; color: white")

        self.board = Board(grid_size, num_of_boxes, num_of_obstacles, json_path)
        self.grid_size = self.board.get_grid_size()

        for texture in self.texture_dict.keys():
            self.texture_dict[texture] = self.texture_dict[texture].scaled(self.board_size // self.grid_size, self.board_size // self.grid_size,
                                                                   Qt.AspectRatioMode.KeepAspectRatio)
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



                if current_pos in boxes_pos:
                    cell.setPixmap(self.texture_dict["box_texture"])
                elif current_pos in goals_pos:
                    cell.setPixmap(self.texture_dict["goal_texture"])
                    curr_texture = self.texture_dict["goal_texture"]
                elif current_pos in obstacles_pos:
                    cell.setPixmap(self.texture_dict["obstacle_texture"])
                else:
                    cell.setPixmap(self.texture_dict["ground_texture"])
                    curr_texture = self.texture_dict["ground_texture"]

                if current_pos == player_pos:
                    combined = curr_texture.copy()
                    painter = QPainter(combined)
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
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(40, 0, 40, 0)

        title = QLabel("Settings")
        title.setStyleSheet("font-size: 28px; font-weight: bold; margin-bottom: 20px")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)

        self.grid_size_slider, self.grid_size_val = self.create_slider_row(main_layout, "Grid size:", 3, 12, 6)
        self.boxes_slider, self.boxes_val = self.create_slider_row(main_layout, "Number of boxes:", 1, 10, 3)
        self.obstacles_slider, self.obstacles_val = self.create_slider_row(main_layout, "Number of obstacles:", 0, 20,5)

        # Creating frame for selecting json file
        file_frame = QFrame()
        file_layout = QHBoxLayout(file_frame)
        self.file_label = QLabel("No JSON file selected")
        self.file_label.setStyleSheet("color: #aaaaaa;")

        btn_select_file = QPushButton("Browse JSON")
        btn_select_file.setFixedWidth(100)
        btn_select_file.clicked.connect(self.handle_file_selection)

        map_label = QLabel("Loaded map:")

        file_layout.addWidget(map_label)
        file_layout.addWidget(self.file_label, stretch=1)
        file_layout.addWidget(btn_select_file)
        main_layout.addWidget(file_frame)

        main_layout.addStretch()

        bottom_layout = QHBoxLayout()
        btn_apply = QPushButton("Apply")
        btn_apply.clicked.connect(self.apply_settings)

        btn_back = QPushButton("Back to menu")
        btn_back.clicked.connect(self.back_to_menu)

        bottom_layout.addWidget(btn_back)
        bottom_layout.addWidget(btn_apply)
        main_layout.addLayout(bottom_layout)

        self.setLayout(main_layout)

        # Setting initial values for game settings
        self.grid_size_final = copy(self.grid_size_slider.value())
        self.num_of_boxes_final = copy(self.boxes_slider.value())
        self.num_of_obstacles_final = copy(self.obstacles_slider.value())
        self.selected_json_path_final = None
        self.selected_json_path = None

    def create_slider_row(self, parent_layout, label_text, min_val, max_val, default_val):
        frame = QFrame()
        layout = QHBoxLayout(frame)

        name_label = QLabel(label_text)
        name_label.setFixedWidth(150)

        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(min_val, max_val)
        slider.setValue(default_val)

        val_label = QLabel(str(default_val))
        val_label.setFixedWidth(30)
        val_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        val_label.setStyleSheet("font-weight: bold; color: #5c9ce6")

        slider.valueChanged.connect(lambda v, l=val_label: l.setText(str(v)))

        layout.addWidget(name_label)
        layout.addWidget(slider)
        layout.addWidget(val_label)

        parent_layout.addWidget(frame)
        return slider, val_label

    def handle_file_selection(self):
        selected_file, _ = QFileDialog.getOpenFileName(self, "Choose map", "", "JSON Files (*.json);;All Files (*)")

        if selected_file:
            selected_path = Path(selected_file)
            if not selected_path.suffix == '.json':
                QMessageBox.warning(self, "Wrong file extension", "Choose .json file.")
                self.file_label.setText("No JSON file selected")
                self.selected_json_path = None
            else:
                self.file_label.setText(selected_path.name)
                self.selected_json_path = selected_path

    def apply_settings(self):
        self.grid_size_final = self.grid_size_slider.value()
        self.num_of_boxes_final = self.boxes_slider.value()
        self.num_of_obstacles_final = self.obstacles_slider.value()
        self.selected_json_path_final = self.selected_json_path

    def back_to_menu(self):
        self.parent_window.stacked_widget.setCurrentIndex(0)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())