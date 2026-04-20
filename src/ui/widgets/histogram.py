import cv2
import numpy as np
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QWidget

_CHANNEL_COLORS = [
    QColor(30, 100, 255, 160),   # B
    QColor(30, 200, 30, 160),    # G
    QColor(255, 60, 60, 160),    # R
]


class HistogramWidget(QWidget):
    HEIGHT = 120

    def __init__(self, parent=None):
        super().__init__(parent)
        self._hists: list[np.ndarray] | None = None
        self.setMinimumHeight(self.HEIGHT)
        self.setMaximumHeight(self.HEIGHT)

    def update_image(self, image: np.ndarray) -> None:
        self._hists = [
            cv2.calcHist([image], [c], None, [256], [0, 256]).flatten()
            for c in range(3)
        ]
        self.update()

    def paintEvent(self, event) -> None:
        if self._hists is None:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()

        max_val = max(hist.max() for hist in self._hists) or 1

        for hist, color in zip(self._hists, _CHANNEL_COLORS):
            painter.setPen(QPen(color, 1))
            for i in range(256):
                bar_h = int(hist[i] / max_val * h)
                x = int(i * w / 256)
                painter.drawLine(x, h, x, h - bar_h)
