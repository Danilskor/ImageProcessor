import cv2
from PySide6.QtWidgets import QComboBox, QFormLayout, QSpinBox

from src.processors.spatial.resize import ResizeTransformation
from src.ui.widgets.processor_controls import BaseProcessorControlWidget, ProcessorControlsRegistry

_INTERP_OPTIONS = [
    ("Linear", cv2.INTER_LINEAR),
    ("Nearest", cv2.INTER_NEAREST),
    ("Cubic", cv2.INTER_CUBIC),
    ("Lanczos4", cv2.INTER_LANCZOS4),
    ("Area", cv2.INTER_AREA),
]


class ResizeControlWidget(BaseProcessorControlWidget):
    def _build_ui(self) -> None:
        layout = QFormLayout(self)
        cfg = self._processor._config

        self._width = QSpinBox()
        self._width.setRange(1, 16000)
        self._width.setValue(cfg.width)

        self._height = QSpinBox()
        self._height.setRange(1, 16000)
        self._height.setValue(cfg.height)

        self._interp = QComboBox()
        for label, code in _INTERP_OPTIONS:
            self._interp.addItem(label, userData=code)
        for i, (_, code) in enumerate(_INTERP_OPTIONS):
            if code == cfg.interpolation:
                self._interp.setCurrentIndex(i)
                break

        self._width.valueChanged.connect(lambda v: (self._processor.update_config(width=v), self.controls_changed.emit()))
        self._height.valueChanged.connect(lambda v: (self._processor.update_config(height=v), self.controls_changed.emit()))
        self._interp.currentIndexChanged.connect(self._interp_changed)

        layout.addRow("Width", self._width)
        layout.addRow("Height", self._height)
        layout.addRow("Interpolation", self._interp)

    def _interp_changed(self, index: int) -> None:
        code = self._interp.itemData(index)
        self._processor.update_config(interpolation=code)
        self.controls_changed.emit()


ProcessorControlsRegistry.register(ResizeTransformation, ResizeControlWidget)
