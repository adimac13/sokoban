from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QPainter


class FactoryEntity:
    def __init__(self, path):
        self.texture = QPixmap(path)

    def resize(self, width, height):
        self.texture = self.texture.scaled(width, height, Qt.AspectRatioMode.KeepAspectRatio)

    def block(self):
        ground_texture = FactoryEntity("./sokoban-assets/environment/ground.png")

        combined = ground_texture.texture
        painter = QPainter(combined)
        painter.drawPixmap(0, 0, self.texture)
        painter.end()
        return ground_texture.texture