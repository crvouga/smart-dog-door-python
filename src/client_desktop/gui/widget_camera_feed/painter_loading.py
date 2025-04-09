from PySide6.QtWidgets import QLabel  # type: ignore
from PySide6.QtGui import QPixmap, QPainter, QColor, QFont  # type: ignore


class PainterLoading:
    _feed_label: QLabel

    def __init__(self, feed_label: QLabel):
        self._feed_label = feed_label

    def draw(self) -> None:
        pixmap = QPixmap(self._feed_label.size())
        pixmap.fill(QColor(0, 0, 0, 50))  # Semi-transparent black

        painter = QPainter(pixmap)
        painter.setPen(QColor(255, 255, 255))

        font = self._feed_label.font()
        font.setPointSize(font.pointSize() * 2)
        font.setWeight(QFont.Bold)
        painter.setFont(font)

        text = "Loading Camera..."
        metrics = painter.fontMetrics()
        text_width = metrics.horizontalAdvance(text)
        text_height = metrics.height()

        x = (pixmap.width() - text_width) // 2
        y = (pixmap.height() + text_height) // 2

        painter.drawText(x, y, text)
        painter.end()

        self._feed_label.setPixmap(pixmap)
