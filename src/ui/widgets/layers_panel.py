import cv2
import numpy as np
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

_THUMB_W = 120
_THUMB_H = 90


def _to_pixmap(image: np.ndarray) -> QPixmap:
    if image.ndim == 2:
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    image = np.ascontiguousarray(image)
    h, w = image.shape[:2]
    q = QImage(image.tobytes(), w, h, image.strides[0], QImage.Format.Format_BGR888)
    return QPixmap.fromImage(q)


class _ThumbItem(QFrame):
    clicked = Signal(str)   # emits step_name

    def __init__(self, step_name: str, image: np.ndarray | None, parent=None):
        super().__init__(parent)
        self._step_name = step_name
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._build_ui(step_name, image)

    def _build_ui(self, display_name: str, image: np.ndarray | None) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(2)

        self._img_label = QLabel()
        self._img_label.setFixedSize(_THUMB_W, _THUMB_H)
        self._img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        name_label = QLabel(display_name)
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_label.setWordWrap(True)

        layout.addWidget(self._img_label)
        layout.addWidget(name_label)

        if image is not None:
            self.set_image(image)

    def set_image(self, image: np.ndarray) -> None:
        px = _to_pixmap(image)
        self._img_label.setPixmap(
            px.scaled(
                _THUMB_W, _THUMB_H,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )

    def set_selected(self, selected: bool) -> None:
        if selected:
            self.setStyleSheet(
                "QFrame { border: 2px solid #4a90d9; border-radius: 3px; background: rgba(74,144,217,0.12); }"
            )
        else:
            self.setStyleSheet("")

    def mousePressEvent(self, event) -> None:
        self.clicked.emit(self._step_name)
        super().mousePressEvent(event)


class LayersPanelWidget(QWidget):
    """Scrollable list of per-step thumbnails.

    Emits layer_view_requested(step_name) when the user clicks a step.
    Emitting "" means "show the full pipeline output" (deselect).
    """

    layer_view_requested = Signal(str)  # step_name or "" for final output

    def __init__(self, parent=None):
        super().__init__(parent)
        self._items: dict[str, _ThumbItem] = {}
        self._selected: str | None = None
        self._build_ui()

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        self._content = QWidget()
        self._vbox = QVBoxLayout(self._content)
        self._vbox.setSpacing(4)
        self._vbox.setContentsMargins(4, 4, 4, 4)
        self._vbox.addStretch()

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self._content)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        outer.addWidget(scroll)

    def update_layers(
        self, step_names: list[str], thumbnails: dict[str, np.ndarray]
    ) -> None:
        """Rebuild thumbnail list to match current pipeline step order."""
        # Remove items that no longer exist
        for name in list(self._items):
            if name not in step_names:
                w = self._items.pop(name)
                self._vbox.removeWidget(w)
                w.deleteLater()

        # Temporarily remove stretch
        stretch = self._vbox.takeAt(self._vbox.count() - 1)

        for i, name in enumerate(step_names):
            if name in self._items:
                item = self._items[name]
                self._vbox.removeWidget(item)
                if name in thumbnails:
                    item.set_image(thumbnails[name])
            else:
                item = _ThumbItem(name, thumbnails.get(name))
                item.clicked.connect(self._on_item_clicked)
                self._items[name] = item
            self._vbox.insertWidget(i, item)

        self._vbox.addStretch()

        # Clear selection if the selected step was removed
        if self._selected is not None and self._selected not in self._items:
            self._selected = None

        self._update_selection_visuals()

    def clear_selection(self) -> None:
        self._selected = None
        self._update_selection_visuals()

    def _on_item_clicked(self, step_name: str) -> None:
        if self._selected == step_name:
            # Toggle off → show final output
            self._selected = None
            self.layer_view_requested.emit("")
        else:
            self._selected = step_name
            self.layer_view_requested.emit(step_name)
        self._update_selection_visuals()

    def _update_selection_visuals(self) -> None:
        for name, item in self._items.items():
            item.set_selected(name == self._selected)
