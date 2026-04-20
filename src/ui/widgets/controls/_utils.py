"""Reusable slider + spinbox row for float parameters."""
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QDoubleSpinBox, QHBoxLayout, QSlider, QWidget


class FloatSliderRow(QWidget):
    """Horizontal slider synced with a spinbox, emits value_changed(float)."""

    value_changed = Signal(float)

    def __init__(
        self,
        min_val: float,
        max_val: float,
        value: float,
        decimals: int = 2,
        scale: int = 100,   # slider integer = float * scale
        parent=None,
    ):
        super().__init__(parent)
        self._scale = scale

        self._slider = QSlider(Qt.Orientation.Horizontal)
        self._slider.setRange(int(min_val * scale), int(max_val * scale))
        self._slider.setValue(int(value * scale))

        self._spin = QDoubleSpinBox()
        self._spin.setRange(min_val, max_val)
        self._spin.setDecimals(decimals)
        self._spin.setSingleStep(1 / scale)
        self._spin.setValue(value)
        self._spin.setFixedWidth(72)

        self._slider.valueChanged.connect(self._from_slider)
        self._spin.valueChanged.connect(self._from_spin)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._slider, stretch=1)
        layout.addWidget(self._spin)

    def value(self) -> float:
        return self._spin.value()

    def set_range(self, min_val: float, max_val: float) -> None:
        self._slider.setRange(int(min_val * self._scale), int(max_val * self._scale))
        self._spin.setRange(min_val, max_val)

    def set_value(self, v: float) -> None:
        self._spin.blockSignals(True)
        self._slider.blockSignals(True)
        self._spin.setValue(v)
        self._slider.setValue(int(v * self._scale))
        self._spin.blockSignals(False)
        self._slider.blockSignals(False)

    def _from_slider(self, raw: int) -> None:
        v = raw / self._scale
        self._spin.blockSignals(True)
        self._spin.setValue(v)
        self._spin.blockSignals(False)
        self.value_changed.emit(v)

    def _from_spin(self, v: float) -> None:
        self._slider.blockSignals(True)
        self._slider.setValue(int(v * self._scale))
        self._slider.blockSignals(False)
        self.value_changed.emit(v)
