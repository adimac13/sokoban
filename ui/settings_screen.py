import json
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog, QMessageBox, QSlider, QFrame, QHBoxLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from pathlib import Path
from copy import copy

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
        self.player_cell.setFixedSize(160, 160)

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

        self.max_a_star_moves = None
        self.max_a_star_moves_final = None
        self.a_star_move_time = None
        self.a_star_move_time_final = None

        self.player1_pixmap = QPixmap("./sokoban-assets/player/playerJ_down.png")
        self.player1_pixmap = self.player1_pixmap.scaled(160,160,Qt.AspectRatioMode.KeepAspectRatio)
        self.player2_pixmap = QPixmap("./sokoban-assets/player/playerA_down.png")
        self.player2_pixmap = self.player2_pixmap.scaled(160, 160, Qt.AspectRatioMode.KeepAspectRatio)

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
                QMessageBox.warning(self, "Error", "Choose .json file.")
                self.file_label.setText("No JSON file selected.")
                self.selected_json_path = None
            else:
                if not self._check_json(selected_file):
                    QMessageBox.warning(self, "Error", "Wrong settings.")
                    self.file_label.setText("No JSON file selected.")
                    self.selected_json_path = None
                else:
                    self.file_label.setText(selected_path.name)
                    self.selected_json_path = selected_path

    def _check_json(self, path):
        """
        Returns 1 if json is correct, else 0.
        """
        with open(str(path), 'r') as f:
            boxes_pos = []
            goals_pos = []
            obstacles_pos = []
            player_pos = []
            data = json.load(f)
            p = data['player']
            b = data['boxes']
            g = data['goals']
            o = data['obstacles']
            s = data['size']
            player_pos.append(tuple(p))
            grid_size = s

            for box in b:
                if box[0] < 0 or box[0] > grid_size - 1 or box[1] < 0 or box[1] > grid_size - 1:
                    return 0
                boxes_pos.append(tuple(box))
            for goal in g:
                if goal[0] < 0 or goal[0] > grid_size - 1 or goal[1] < 0 or goal[1] > grid_size - 1:
                    return 0
                goals_pos.append(tuple(goal))
            for obstacle in o:
                if obstacle[0] < 0 or obstacle[0] > grid_size - 1 or obstacle[1] < 0 or obstacle[1] > grid_size - 1:
                    return 0
                obstacles_pos.append(tuple(obstacle))


        b_g = (set(boxes_pos) & set(goals_pos)) | (set(boxes_pos) & set(player_pos))
        b_o = (set(boxes_pos) & set(obstacles_pos)) | (set(obstacles_pos) & set(player_pos))
        g_o = (set(goals_pos) & set(obstacles_pos)) | (set(goals_pos) & set(player_pos))

        if len(b_g) or len(b_o) or len(g_o) or grid_size**2 < (len(boxes_pos) + len(goals_pos) + len(obstacles_pos) + 1):
            # Some positions overlap
            return 0
        else:
            # Positions dont overlap
            if "a_star_move_time" in data:
                self.a_star_move_time = data["a_star_move_time"]
            else:
                self.a_star_move_time = None

            if "max_a_star_moves" in data:
                self.max_a_star_moves = data["max_a_star_moves"]
            else:
                self.max_a_star_moves = None

            return 1

    def apply_settings(self):
        if self.grid_size_slider.value() ** 2 > self.boxes_slider.value() + self.obstacles_slider.value():
            self.grid_size_final = self.grid_size_slider.value()
            self.num_of_boxes_final = self.boxes_slider.value()
            self.num_of_obstacles_final = self.obstacles_slider.value()
            self.selected_json_path_final = self.selected_json_path
            self.selected_player_final = self.selected_player
            self.a_star_move_time_final = self.a_star_move_time
            self.max_a_star_moves_final = self.max_a_star_moves
            QMessageBox.information(self, "Done", "Successfully applied.")
        else:
            QMessageBox.warning(self, "Wrong settings", "Could not apply changes because of wrong values.")

    def back_to_menu(self):
        self.parent_window.stacked_widget.setCurrentIndex(0)