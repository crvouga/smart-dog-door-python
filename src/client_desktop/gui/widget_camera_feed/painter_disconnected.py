from PySide6.QtWidgets import QLabel  # type: ignore
from PySide6.QtGui import QPixmap, QPainter, QColor, QFont  # type: ignore


class PainterDisconnected:
    _feed_label: QLabel

    def __init__(self, feed_label: QLabel):
        self._feed_label = feed_label

    def draw(self) -> None:
        # Create a red background with "Camera Disconnected" text
        pixmap = QPixmap(self._feed_label.size())
        pixmap.fill(QColor(255, 0, 0, 50))  # Semi-transparent red

        painter = QPainter(pixmap)
        painter.setPen(QColor(255, 255, 255))

        # Create a larger, bolder font
        font = self._feed_label.font()
        font.setPointSize(font.pointSize() * 2)  # Double the font size
        font.setWeight(QFont.Weight.Bold)  # Make it bold
        painter.setFont(font)

        text = "Camera Disconnected"
        metrics = painter.fontMetrics()
        text_width = metrics.horizontalAdvance(text)
        text_height = metrics.height()

        x = (pixmap.width() - text_width) // 2
        y = (pixmap.height() + text_height) // 2

        painter.drawText(x, y, text)
        painter.end()

        self._feed_label.setPixmap(pixmap)
