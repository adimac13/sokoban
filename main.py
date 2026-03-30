import sys
from PyQt6.QtWidgets import QApplication
from ui.window import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

# If you want to compile to exe run:
# pyinstaller --onefile --noconsole --icon=icon.ico --add-data "sokoban-assets;sokoban-assets" main.py