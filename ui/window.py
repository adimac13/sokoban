import sys
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtWidgets import QMainWindow, QStackedWidget, QWidget, QVBoxLayout, QPushButton, QLabel, \
    QGridLayout, QFileDialog, QMessageBox, QSlider, QFrame, QHBoxLayout
from PyQt6.QtCore import Qt, QTimer, QUrl
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

        # Setting up soundtrack
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        self.player.setSource(QUrl.fromLocalFile("./sokoban-assets/soundtrack/soundtrack.mp3"))
        self.audio_output.setVolume(0.2)
        self.player.setLoops(-1)
        self.player.play()


class MenuScreen(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel("Sokoban")
        title.setStyleSheet("font-size: 34px; font-weight: bold; font-family: 'Courier New', monospace;")
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
                                            self.parent.settings_screen.num_of_obstacles_final, self.parent.settings_screen.selected_json_path_final,
                                            self.parent.settings_screen.selected_player_final)

        self.parent.stacked_widget.setCurrentIndex(1)

    def go_to_settings(self):
        # Setting idx for 2
        self.parent.settings_screen.setup()

        self.parent.stacked_widget.setCurrentIndex(2)

class GameScreen(QWidget):
    def __init__(self, parent_window):
        super().__init__()

        self.board = None

        # Creating dict so that it can be later modified
        self.texture_dict = {
            "ground_texture" : QPixmap("./sokoban-assets/environment/ground.png"),
            "box_texture" : QPixmap("./sokoban-assets/environment/box.png"),
            "goal_texture" : QPixmap("./sokoban-assets/environment/goal.png"),
            "obstacle_texture" : QPixmap("./sokoban-assets/environment/obstacle.png"),
            "box_on_goal_texture" : QPixmap("./sokoban-assets/environment/box_on_goal.png")
        }

        self.board_size = 300
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

    def setup_board(self, grid_size, num_of_boxes, num_of_obstacles, json_path, selected_player):
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

        self.board = Board(grid_size, num_of_boxes, num_of_obstacles, json_path)
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


                if current_pos in boxes_pos and current_pos in goals_pos:
                    cell.setPixmap(self.texture_dict["box_on_goal_texture"])
                elif current_pos in boxes_pos:
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
            QTimer.singleShot(400, self.a_star_solver)
        else:
            pass

    def back_to_menu(self):
        self.timer.stop()
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

        self.grid_size_slider, self.grid_size_val = self.create_slider_row(main_layout, "Grid size:", 4, 12, 6)
        self.boxes_slider, self.boxes_val = self.create_slider_row(main_layout, "Number of boxes:", 1, 10, 3)
        self.obstacles_slider, self.obstacles_val = self.create_slider_row(main_layout, "Number of obstacles:", 0, 20,5)

        # Creating frame for selecting json file
        file_frame = QFrame()
        file_layout = QHBoxLayout(file_frame)
        self.file_label = QLabel("No JSON file selected.")
        self.file_label.setStyleSheet("color: #aaaaaa;")

        btn_select_file = QPushButton("Browse JSON")
        btn_select_file.setFixedWidth(100)
        btn_select_file.clicked.connect(self.handle_file_selection)

        btn_remove_file = QPushButton("Remove JSON")
        btn_remove_file.setFixedWidth(100)
        btn_remove_file.clicked.connect(self.handle_file_remove)

        map_label = QLabel("Loaded map:")

        file_layout.addWidget(map_label)
        file_layout.addWidget(self.file_label, stretch=1)
        file_layout.addWidget(btn_remove_file)
        file_layout.addWidget(btn_select_file)
        main_layout.addWidget(file_frame)

        main_layout.addStretch()


        # Bottom layout
        bottom_layout = QHBoxLayout()
        btn_apply = QPushButton("Apply")
        btn_apply.clicked.connect(self.apply_settings)
        btn_apply.setFixedSize(150, 40)

        btn_back = QPushButton("Back to menu")
        btn_back.clicked.connect(self.back_to_menu)
        btn_back.setFixedSize(150, 40)

        self.btn_mute = QPushButton("Mute")
        self.btn_mute.setFixedSize(150, 40)
        self.btn_mute.setStyleSheet("background-color: #e87474;")
        self.btn_mute.clicked.connect(self.change_volume)

        bottom_layout.addWidget(btn_back)
        bottom_layout.addWidget(btn_apply)
        bottom_layout.addWidget(self.btn_mute)

        main_layout.addLayout(bottom_layout)
        main_layout.addSpacing(300)

        # Layout for choosing player skin
        player_layout = QHBoxLayout()

        self.btn_playerJ = QPushButton("Player 1")
        self.btn_playerJ.setFixedSize(150, 40)
        self.btn_playerJ.clicked.connect(self.choose_p1)
        self.btn_playerJ.setStyleSheet("background-color: #447387;")

        self.btn_playerA = QPushButton("Player 2")
        self.btn_playerA.setFixedSize(150, 40)
        self.btn_playerA.clicked.connect(self.choose_p2)


        self.player_cell = QLabel()
        self.player_cell.setFixedSize(80, 80)
        self.player_cell.setStyleSheet("border: 1px solid darkgray;")

        player_layout.addWidget(self.btn_playerJ)
        player_layout.addWidget(self.btn_playerA)
        player_layout.addWidget(self.player_cell)
        main_layout.addLayout(player_layout)
        main_layout.addSpacing(400)

        self.setLayout(main_layout)

        # Setting initial values for game settings
        self.grid_size_final = copy(self.grid_size_slider.value())
        self.num_of_boxes_final = copy(self.boxes_slider.value())
        self.num_of_obstacles_final = copy(self.obstacles_slider.value())
        self.selected_json_path_final = None
        self.selected_json_path = None
        self.selected_player = 1
        self.selected_player_final = 1
        self.player1_pixmap = QPixmap("./sokoban-assets/player/playerJ_down.png")
        self.player1_pixmap = self.player1_pixmap.scaled(80,80,Qt.AspectRatioMode.KeepAspectRatio)
        self.player2_pixmap = QPixmap("./sokoban-assets/player/playerA_down.png")
        self.player2_pixmap = self.player2_pixmap.scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatio)

    def set_skin(self):
        if self.selected_player == 1:
            self.player_cell.setPixmap(self.player1_pixmap)
        else:
            self.player_cell.setPixmap(self.player2_pixmap)

    def choose_p1(self):
        self.selected_player = 1
        self.set_skin()
        self.btn_playerJ.setStyleSheet("background-color: #447387;")
        self.btn_playerA.setStyleSheet("")

    def choose_p2(self):
        self.selected_player = 2
        self.set_skin()
        self.btn_playerA.setStyleSheet("background-color: #447387;")
        self.btn_playerJ.setStyleSheet("")

    def setup(self):
        if self.selected_player == 1:
            self.player_cell.setPixmap(self.player1_pixmap)
        else:
            self.player_cell.setPixmap(self.player2_pixmap)


    def handle_file_remove(self):
        self.selected_json_path = None
        self.selected_json_path_final = None
        self.file_label.setText("No JSON file selected.")
        QMessageBox.information(self, "Done", "Successfully removed JSON.")

    def change_volume(self):
        current_style = self.btn_mute.styleSheet()

        if current_style == "background-color: #e87474;":
            self.btn_mute.setText("Unmute")
            self.btn_mute.setStyleSheet("background-color: green;")
            self.parent_window.audio_output.setVolume(0.0)
        else:
            self.btn_mute.setText("Mute")
            self.btn_mute.setStyleSheet("background-color: #e87474;")
            self.parent_window.audio_output.setVolume(0.2)



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
                self.file_label.setText("No JSON file selected.")
                self.selected_json_path = None
            else:
                self.file_label.setText(selected_path.name)
                self.selected_json_path = selected_path

    def apply_settings(self):
        if self.grid_size_slider.value() ** 2 > self.boxes_slider.value() + self.obstacles_slider.value():
            self.grid_size_final = self.grid_size_slider.value()
            self.num_of_boxes_final = self.boxes_slider.value()
            self.num_of_obstacles_final = self.obstacles_slider.value()
            self.selected_json_path_final = self.selected_json_path
            self.selected_player_final = self.selected_player
            QMessageBox.information(self, "Done", "Successfully applied.")
        else:
            QMessageBox.warning(self, "Wrong settings", "Could not apply changes because of wrong values.")

    def back_to_menu(self):
        self.parent_window.stacked_widget.setCurrentIndex(0)

if __name__ == "__main__":
    pass