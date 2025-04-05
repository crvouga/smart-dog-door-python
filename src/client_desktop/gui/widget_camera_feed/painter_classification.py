from PySide6.QtGui import QPainter, QPen, QColor  # type: ignore
from src.image_classifier.classification import Classification


class PainterClassification:
    def __init__(self, painter: QPainter):
        self._painter = painter
        self._setup_painter()

    def _setup_painter(self) -> None:
        pen = QPen(QColor(255, 0, 0))
        pen.setWidth(2)
        self._painter.setPen(pen)

    def draw(
        self, classification: Classification, scale_x: float, scale_y: float
    ) -> None:
        bbox = classification.bounding_box

        rect_x = int(bbox.x_min * scale_x)
        rect_y = int(bbox.y_min * scale_y)
        rect_w = int((bbox.x_max - bbox.x_min) * scale_x)
        rect_h = int((bbox.y_max - bbox.y_min) * scale_y)

        if rect_w > 0 and rect_h > 0:
            self._draw_bounding_box(rect_x, rect_y, rect_w, rect_h)
            self._draw_label(classification, rect_x, rect_y)

    def _draw_bounding_box(self, x: int, y: int, width: int, height: int) -> None:
        self._painter.drawRect(x, y, width, height)

    def _draw_label(
        self, classification: Classification, rect_x: int, rect_y: int
    ) -> None:
        label_text = f"{classification.label} ({classification.weight:.2f})"
        text_x = rect_x
        text_y = rect_y - 5 if rect_y > 10 else rect_y + 15
        self._painter.drawText(text_x, text_y, label_text)
