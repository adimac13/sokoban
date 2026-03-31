from PyQt6.QtGui import QPixmap


class FactoryEntity:
    def __init__(self, path):
        self.texture = QPixmap(path)

    def resize(self, width, height):
        self.texture = self.texture.scaled(width, height, Qt.AspectRatioMode.KeepAspectRatio)

    def block(self, texture):
