from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtWidgets import QMainWindow, QStackedWidget
from PyQt6.QtCore import QUrl

from .menu_screen import MenuScreen
from .singleplayer_screen import SinglePlayerScreen
from .multiplayer_screen import MultiPlayerScreen
from .settings_screen import SettingsScreen

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sokoban")
        self.setFixedSize(1200, 900)
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # Creating two different screens
        self.menu_screen = MenuScreen(self)
        self.game_single_screen = SinglePlayerScreen(self)
        self.settings_screen = SettingsScreen(self)
        self.game_multi_screen = MultiPlayerScreen(self)

        self.grid_size = self.settings_screen.grid_size_final

        # 0 -> menu, 1 -> singleplayer, 2 -> settings, 3-> multiplayer
        self.stacked_widget.addWidget(self.menu_screen)
        self.stacked_widget.addWidget(self.game_single_screen)
        self.stacked_widget.addWidget(self.settings_screen)
        self.stacked_widget.addWidget(self.game_multi_screen)

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

if __name__ == "__main__":
    pass