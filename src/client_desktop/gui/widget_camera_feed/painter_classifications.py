from PySide6.QtGui import QPainter, QPen, QColor, QFont  # type: ignore
from PySide6.QtCore import Qt
from src.image_classifier.classification import Classification


DEFAULT_BOUNDING_BOX_COLOR = QColor(255, 0, 0)
DEFAULT_LABEL_COLOR = QColor(255, 0, 0)
DEFAULT_TEXT_COLOR = QColor(255, 255, 255)
BOUNDING_BOX_WIDTH = 3
FONT_SIZE = 12
LABEL_PADDING = 4
LABEL_OFFSET_TOP = 5
LABEL_OFFSET_BOTTOM = 15
LABEL_THRESHOLD = 10
LABEL_TEXT_FORMAT = "{label} ({weight:.2f})"
LABEL_COLORS = {
    "dog": QColor(0, 128, 0),
    "cat": QColor(255, 0, 0),
}
BORDER_RADIUS = 5


class PainterClassifications:
    def __init__(self, painter: QPainter):
        self._painter = painter
        self._setup_painter()

    def _setup_painter(self) -> None:
        pen = QPen(DEFAULT_BOUNDING_BOX_COLOR)
        pen.setWidth(BOUNDING_BOX_WIDTH)
        self._painter.setPen(pen)

        font = QFont()
        font.setBold(True)
        font.setPointSize(FONT_SIZE)
        self._painter.setFont(font)

    def draw(
        self, classification: Classification, scale_x: float, scale_y: float
    ) -> None:
        bbox = classification.bounding_box

        rect_x = int(bbox.x_min * scale_x)
        rect_y = int(bbox.y_min * scale_y)
        rect_w = int((bbox.x_max - bbox.x_min) * scale_x)
        rect_h = int((bbox.y_max - bbox.y_min) * scale_y)

        if rect_w > 0 and rect_h > 0:
            self._draw_bounding_box(classification, rect_x, rect_y, rect_w, rect_h)
            self._draw_label(classification, rect_x, rect_y, rect_w)

    def _draw_bounding_box(
        self, classification: Classification, x: int, y: int, width: int, height: int
    ) -> None:
        color = LABEL_COLORS.get(classification.label, DEFAULT_BOUNDING_BOX_COLOR)
        pen = QPen(color)
        pen.setWidth(BOUNDING_BOX_WIDTH)
        self._painter.setPen(pen)
        self._painter.setBrush(Qt.NoBrush)
        self._painter.drawRoundedRect(x, y, width, height, BORDER_RADIUS, BORDER_RADIUS)

    def _draw_label(
        self, classification: Classification, rect_x: int, rect_y: int, rect_w: int
    ) -> None:
        label_text = LABEL_TEXT_FORMAT.format(
            label=classification.label, weight=classification.weight
        )

        metrics = self._painter.fontMetrics()
        text_width = metrics.horizontalAdvance(label_text)
        text_height = metrics.height()

        text_x = rect_x + (rect_w - text_width) // 2
        text_y = (
            rect_y - LABEL_OFFSET_TOP
            if rect_y > LABEL_THRESHOLD
            else rect_y + LABEL_OFFSET_BOTTOM
        )

        background_color = LABEL_COLORS.get(classification.label, DEFAULT_LABEL_COLOR)
        self._painter.setPen(Qt.NoPen)
        self._painter.setBrush(background_color)
        self._painter.drawRoundedRect(
            text_x - LABEL_PADDING,
            text_y - text_height - LABEL_PADDING,
            text_width + 2 * LABEL_PADDING,
            text_height + 2 * LABEL_PADDING,
            BORDER_RADIUS,
            BORDER_RADIUS,
        )

        self._painter.setPen(DEFAULT_TEXT_COLOR)

        self._painter.drawText(
            text_x - LABEL_PADDING + (text_width + 2 * LABEL_PADDING - text_width) // 2,
            text_y
            - LABEL_PADDING
            + (text_height + 2 * LABEL_PADDING - text_height) // 2
            - 2,
            label_text,
        )
