from PySide6.QtCore import Signal
from PySide6.QtWidgets import QFormLayout, QLabel, QSpinBox

from src.processors.spatial.crop import CropTransformation
from src.ui.widgets.processor_controls import BaseProcessorControlWidget, ProcessorControlsRegistry


class CropControlWidget(BaseProcessorControlWidget):
    # Emitted when spinboxes change so the viewer overlay can follow
    rect_changed_by_ui = Signal(int, int, int, int)   # x, y, w, h

    def _build_ui(self) -> None:
        layout = QFormLayout(self)
        cfg = self._processor._config

        hint = QLabel("Drag on image to select region")
        hint.setObjectName("dim")
        layout.addRow(hint)

        self._x = QSpinBox(); self._x.setRange(0, 16000); self._x.setValue(cfg.x)
        self._y = QSpinBox(); self._y.setRange(0, 16000); self._y.setValue(cfg.y)
        self._w = QSpinBox(); self._w.setRange(1, 16000); self._w.setValue(cfg.width)
        self._h = QSpinBox(); self._h.setRange(1, 16000); self._h.setValue(cfg.height)

        self._x.valueChanged.connect(self._on_ui_change)
        self._y.valueChanged.connect(self._on_ui_change)
        self._w.valueChanged.connect(self._on_ui_change)
        self._h.valueChanged.connect(self._on_ui_change)

        layout.addRow("X", self._x)
        layout.addRow("Y", self._y)
        layout.addRow("Width", self._w)
        layout.addRow("Height", self._h)

    def _on_ui_change(self) -> None:
        x, y, w, h = self._x.value(), self._y.value(), self._w.value(), self._h.value()
        self._processor.update_config(x=x, y=y, width=w, height=h)
        self.rect_changed_by_ui.emit(x, y, w, h)
        self.controls_changed.emit()

    def set_rect_from_viewer(self, x: int, y: int, w: int, h: int) -> None:
        """Called when user drags on the image — update spinboxes silently."""
        for spin, val in ((self._x, x), (self._y, y), (self._w, w), (self._h, h)):
            spin.blockSignals(True)
            spin.setValue(val)
            spin.blockSignals(False)
        self._processor.update_config(x=x, y=y, width=w, height=h)
        self.controls_changed.emit()


ProcessorControlsRegistry.register(CropTransformation, CropControlWidget)
