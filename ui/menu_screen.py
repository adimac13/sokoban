import sys
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton

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
        btn_play = QPushButton("Singleplayer")
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
        self.parent.game_single_screen.setup_board(self.parent.settings_screen.grid_size_final,
                                                self.parent.settings_screen.num_of_boxes_final,
                                                self.parent.settings_screen.num_of_obstacles_final,
                                                self.parent.settings_screen.selected_json_path_final,
                                                self.parent.settings_screen.selected_player_final, self.parent.settings_screen.a_star_move_time_final,
                                                self.parent.settings_screen.max_a_star_moves_final)


        self.parent.stacked_widget.setCurrentIndex(1)

    def go_to_settings(self):
        # Setting idx for 2
        self.parent.settings_screen.setup()

        self.parent.stacked_widget.setCurrentIndex(2)