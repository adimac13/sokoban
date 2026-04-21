import sys
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QMessageBox


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
        btn_singleplayer = QPushButton("Singleplayer")
        btn_singleplayer.setToolTip("Set up map in settings and play!")
        btn_ai = QPushButton("AI mode")
        btn_ai.setToolTip("Co-op with ai on 6x6 board with 3 goals and 3 obstacles!")
        btn_multiplayer = QPushButton("Multiplayer")
        btn_multiplayer.setToolTip("Play with someone else using TCP!")
        btn_exit = QPushButton("Exit")
        btn_settings = QPushButton("Settings")
        btn_settings.setToolTip("Set the settings for the map in singleplayer mode!")

        for btn in (btn_singleplayer, btn_ai,btn_multiplayer, btn_settings, btn_exit):
            btn.setFixedSize(200, 40)

        btn_singleplayer.clicked.connect(self.go_to_game)
        btn_ai.clicked.connect(self.go_to_ai)
        btn_multiplayer.clicked.connect(self.go_to_multiplayer)
        btn_settings.clicked.connect(self.go_to_settings)
        btn_exit.clicked.connect(sys.exit)

        # Visuals
        layout.addWidget(title)
        layout.addWidget(btn_singleplayer)
        layout.addWidget(btn_multiplayer)
        layout.addWidget(btn_ai)
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

    def go_to_ai(self):
        self.parent.game_ai_screen.setup_board(self.parent.settings_screen.grid_size_final,
                                                   self.parent.settings_screen.num_of_boxes_final,
                                                   self.parent.settings_screen.num_of_obstacles_final,
                                                   self.parent.settings_screen.selected_json_path_final,
                                                   self.parent.settings_screen.selected_player_final,
                                                   self.parent.settings_screen.a_star_move_time_final,
                                                   self.parent.settings_screen.max_a_star_moves_final)
        self.parent.stacked_widget.setCurrentIndex(4)

    def go_to_settings(self):
        # Setting idx for 2
        self.parent.settings_screen.setup()
        self.parent.stacked_widget.setCurrentIndex(2)

    def go_to_multiplayer(self):
        try:
            self.parent.game_multi_screen.setup_board()
            self.parent.stacked_widget.setCurrentIndex(3)
        except:
            QMessageBox.warning(self, "Connection failed", "Could not connect to server.")