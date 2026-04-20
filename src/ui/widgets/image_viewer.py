from __future__ import annotations

import numpy as np
from PySide6.QtCore import QPointF, QRectF, Qt, Signal
from PySide6.QtGui import (
    QColor, QCursor, QImage, QPainter, QPen, QPixmap, QWheelEvent,
)
from PySide6.QtWidgets import (
    QGraphicsItem, QGraphicsObject, QGraphicsPixmapItem,
    QGraphicsScene, QGraphicsView,
)

# ── Crop overlay ──────────────────────────────────────────────────────────────

_HANDLE_R   = 6.0   # handle circle radius (scene units == pixels)
_HANDLE_HIT = 10.0  # hit-test radius
_DIM_COLOR  = QColor(0, 0, 0, 130)
_BORDER_PEN = QPen(QColor(255, 255, 255, 220), 1.5, Qt.PenStyle.DashLine)
_HANDLE_PEN = QPen(QColor(255, 255, 255, 240), 1.5)
_HANDLE_FILL = QColor(80, 140, 255, 220)

# Corner/edge handle indices
_TL, _TR, _BR, _BL = 0, 1, 2, 3

_RESIZE_CURSORS = {
    _TL: Qt.CursorShape.SizeFDiagCursor,
    _TR: Qt.CursorShape.SizeBDiagCursor,
    _BR: Qt.CursorShape.SizeFDiagCursor,
    _BL: Qt.CursorShape.SizeBDiagCursor,
}


class _CropOverlay(QGraphicsObject):
    """Interactive crop-selection overlay drawn on top of the image."""

    rect_changed = Signal(int, int, int, int)   # x, y, w, h  (image coords)

    def __init__(self, image_w: int, image_h: int, parent=None):
        super().__init__(parent)
        self._img_w = image_w
        self._img_h = image_h
        self._rect = QRectF(0, 0, image_w, image_h)

        self._drag_mode = "none"   # none | draw | move | resize_TL/TR/BL/BR
        self._drag_start = QPointF()
        self._rect_at_drag_start = QRectF()

        self.setAcceptHoverEvents(True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)

    # ── QGraphicsItem interface ───────────────────────────────────────────────

    def boundingRect(self) -> QRectF:
        return QRectF(0, 0, self._img_w, self._img_h)

    def paint(self, painter: QPainter, option, widget=None) -> None:
        r = self._rect

        # ── dim areas outside the crop rect ──────────────────────────────────
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(_DIM_COLOR)
        full = QRectF(0, 0, self._img_w, self._img_h)
        # top / bottom / left / right strips
        painter.drawRect(QRectF(0, 0, self._img_w, r.top()))
        painter.drawRect(QRectF(0, r.bottom(), self._img_w, self._img_h - r.bottom()))
        painter.drawRect(QRectF(0, r.top(), r.left(), r.height()))
        painter.drawRect(QRectF(r.right(), r.top(), self._img_w - r.right(), r.height()))

        # ── dashed border ─────────────────────────────────────────────────────
        painter.setPen(_BORDER_PEN)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRect(r)

        # ── rule-of-thirds grid ───────────────────────────────────────────────
        thirds_pen = QPen(QColor(255, 255, 255, 55), 0.8, Qt.PenStyle.SolidLine)
        painter.setPen(thirds_pen)
        for f in (1/3, 2/3):
            x = r.left() + r.width() * f
            y = r.top() + r.height() * f
            painter.drawLine(QPointF(x, r.top()), QPointF(x, r.bottom()))
            painter.drawLine(QPointF(r.left(), y), QPointF(r.right(), y))

        # ── corner handles ────────────────────────────────────────────────────
        painter.setPen(_HANDLE_PEN)
        painter.setBrush(_HANDLE_FILL)
        for pt in self._handle_positions():
            painter.drawEllipse(pt, _HANDLE_R, _HANDLE_R)

    # ── Public API ────────────────────────────────────────────────────────────

    def set_rect(self, x: int, y: int, w: int, h: int) -> None:
        self._rect = self._clamp(QRectF(x, y, max(1, w), max(1, h)))
        self.update()

    def get_rect(self) -> tuple[int, int, int, int]:
        r = self._rect
        return int(r.x()), int(r.y()), int(r.width()), int(r.height())

    # ── Mouse events ──────────────────────────────────────────────────────────

    def hoverMoveEvent(self, event) -> None:
        h = self._hit_handle(event.pos())
        if h is not None:
            self.setCursor(QCursor(_RESIZE_CURSORS[h]))
        elif self._rect.contains(event.pos()):
            self.setCursor(QCursor(Qt.CursorShape.SizeAllCursor))
        else:
            self.setCursor(QCursor(Qt.CursorShape.CrossCursor))

    def mousePressEvent(self, event) -> None:
        if event.button() != Qt.MouseButton.LeftButton:
            return
        pos = event.pos()
        self._drag_start = pos
        self._rect_at_drag_start = QRectF(self._rect)

        h = self._hit_handle(pos)
        if h is not None:
            self._drag_mode = f"resize_{h}"
        elif self._rect.contains(pos):
            self._drag_mode = "move"
        else:
            self._drag_mode = "draw"
            self._rect = self._clamp(QRectF(pos, pos))
            self.update()

    def mouseMoveEvent(self, event) -> None:
        if self._drag_mode == "none":
            return
        pos = event.pos()
        dx = pos.x() - self._drag_start.x()
        dy = pos.y() - self._drag_start.y()
        r0 = self._rect_at_drag_start
        W, H = float(self._img_w), float(self._img_h)

        if self._drag_mode == "draw":
            # Clamp both endpoints to image bounds before building the rect
            ax = max(0.0, min(self._drag_start.x(), W))
            ay = max(0.0, min(self._drag_start.y(), H))
            bx = max(0.0, min(pos.x(), W))
            by = max(0.0, min(pos.y(), H))
            x, w = (ax, bx - ax) if bx >= ax else (bx, ax - bx)
            y, h = (ay, by - ay) if by >= ay else (by, ay - by)
            self._rect = QRectF(x, y, max(1.0, w), max(1.0, h))

        elif self._drag_mode == "move":
            self._rect = self._clamp_move(
                QRectF(r0.x() + dx, r0.y() + dy, r0.width(), r0.height())
            )

        elif self._drag_mode == f"resize_{_TL}":
            nx = max(0.0, min(r0.left() + dx, r0.right() - 1))
            ny = max(0.0, min(r0.top()  + dy, r0.bottom() - 1))
            self._rect = QRectF(nx, ny, r0.right() - nx, r0.bottom() - ny)

        elif self._drag_mode == f"resize_{_TR}":
            ny  = max(0.0, min(r0.top() + dy, r0.bottom() - 1))
            nr  = min(W, max(r0.left() + 1, r0.right() + dx))
            self._rect = QRectF(r0.left(), ny, nr - r0.left(), r0.bottom() - ny)

        elif self._drag_mode == f"resize_{_BR}":
            nr  = min(W, max(r0.left() + 1, r0.right()  + dx))
            nb  = min(H, max(r0.top()  + 1, r0.bottom() + dy))
            self._rect = QRectF(r0.left(), r0.top(), nr - r0.left(), nb - r0.top())

        elif self._drag_mode == f"resize_{_BL}":
            nx  = max(0.0, min(r0.left() + dx, r0.right() - 1))
            nb  = min(H, max(r0.top() + 1, r0.bottom() + dy))
            self._rect = QRectF(nx, r0.top(), r0.right() - nx, nb - r0.top())

        self.update()

    def mouseReleaseEvent(self, event) -> None:
        if event.button() != Qt.MouseButton.LeftButton:
            return
        self._drag_mode = "none"
        x, y, w, h = self.get_rect()
        self.rect_changed.emit(x, y, w, h)

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _handle_positions(self) -> list[QPointF]:
        r = self._rect
        return [
            r.topLeft(), r.topRight(),
            r.bottomRight(), r.bottomLeft(),
        ]

    def _hit_handle(self, pos: QPointF) -> int | None:
        for idx, pt in enumerate(self._handle_positions()):
            if (pos - pt).manhattanLength() <= _HANDLE_HIT:
                return idx
        return None

    def _clamp(self, r: QRectF) -> QRectF:
        x = max(0.0, min(r.x(), self._img_w - 1))
        y = max(0.0, min(r.y(), self._img_h - 1))
        w = max(1.0, min(r.width(), self._img_w - x))
        h = max(1.0, min(r.height(), self._img_h - y))
        return QRectF(x, y, w, h)

    def _clamp_move(self, r: QRectF) -> QRectF:
        x = max(0.0, min(r.x(), self._img_w - r.width()))
        y = max(0.0, min(r.y(), self._img_h - r.height()))
        return QRectF(x, y, r.width(), r.height())


# ── Main viewer ───────────────────────────────────────────────────────────────

class ImageViewerWidget(QGraphicsView):
    ZOOM_FACTOR = 1.15

    crop_rect_changed = Signal(int, int, int, int)  # x, y, w, h

    def __init__(self, parent=None):
        super().__init__(parent)
        self._scene = QGraphicsScene(self)
        self._pixmap_item = QGraphicsPixmapItem()
        self._scene.addItem(self._pixmap_item)
        self.setScene(self._scene)

        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)

        self._crop_overlay: _CropOverlay | None = None
        self._crop_mode = False

    # ── Normal image display ──────────────────────────────────────────────────

    def set_image(self, image: np.ndarray) -> None:
        image = np.ascontiguousarray(image)
        h, w = image.shape[:2]
        stride = image.strides[0]
        q_image = QImage(image.tobytes(), w, h, stride, QImage.Format.Format_BGR888)
        self._pixmap_item.setPixmap(QPixmap.fromImage(q_image))
        self._scene.setSceneRect(self._pixmap_item.boundingRect())

    def fit_in_view(self) -> None:
        if not self._pixmap_item.pixmap().isNull():
            self.fitInView(self._pixmap_item, Qt.AspectRatioMode.KeepAspectRatio)

    # ── Crop mode ─────────────────────────────────────────────────────────────

    def enter_crop_mode(
        self, image: np.ndarray, x: int, y: int, w: int, h: int
    ) -> None:
        """Show `image` (pre-crop) and display an interactive selection overlay."""
        self.set_image(image)
        img_h, img_w = image.shape[:2]

        if self._crop_overlay is not None:
            self._scene.removeItem(self._crop_overlay)

        self._crop_overlay = _CropOverlay(img_w, img_h)
        self._crop_overlay.setZValue(10)
        self._crop_overlay.set_rect(x, y, w, h)
        self._crop_overlay.rect_changed.connect(self.crop_rect_changed)
        self._scene.addItem(self._crop_overlay)

        self._crop_mode = True
        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        self.viewport().setCursor(Qt.CursorShape.CrossCursor)

    def exit_crop_mode(self) -> None:
        if self._crop_overlay is not None:
            self._scene.removeItem(self._crop_overlay)
            self._crop_overlay = None
        self._crop_mode = False
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.viewport().unsetCursor()

    def update_crop_rect(self, x: int, y: int, w: int, h: int) -> None:
        """Called when spinboxes change — update the overlay without emitting."""
        if self._crop_overlay is not None:
            self._crop_overlay.set_rect(x, y, w, h)

    def refresh_crop_image(self, image: np.ndarray) -> None:
        """Re-display the pre-crop image (after upstream steps changed)."""
        if self._crop_mode:
            # Update pixmap but keep overlay
            image = np.ascontiguousarray(image)
            h, w = image.shape[:2]
            stride = image.strides[0]
            q_image = QImage(image.tobytes(), w, h, stride, QImage.Format.Format_BGR888)
            self._pixmap_item.setPixmap(QPixmap.fromImage(q_image))

    # ── Wheel zoom (works in both modes) ─────────────────────────────────────

    def wheelEvent(self, event: QWheelEvent) -> None:
        if event.angleDelta().y() > 0:
            self.scale(self.ZOOM_FACTOR, self.ZOOM_FACTOR)
        else:
            self.scale(1 / self.ZOOM_FACTOR, 1 / self.ZOOM_FACTOR)
