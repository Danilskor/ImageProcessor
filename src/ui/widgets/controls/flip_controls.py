from PySide6.QtWidgets import QComboBox, QFormLayout

from src.processors.spatial.flip import FlipTransformation
from src.ui.widgets.processor_controls import BaseProcessorControlWidget, ProcessorControlsRegistry

_OPTIONS = [
    ("Horizontal (left ↔ right)", 1),
    ("Vertical (top ↔ bottom)", 0),
    ("Both", -1),
]


class FlipControlWidget(BaseProcessorControlWidget):
    def _build_ui(self) -> None:
        layout = QFormLayout(self)
        cfg = self._processor._config

        self._combo = QComboBox()
        for label, code in _OPTIONS:
            self._combo.addItem(label, userData=code)

        current_code = cfg.flip_code
        for i, (_, code) in enumerate(_OPTIONS):
            if code == current_code:
                self._combo.setCurrentIndex(i)
                break

        self._combo.currentIndexChanged.connect(self._changed)
        layout.addRow("Direction", self._combo)

    def _changed(self, index: int) -> None:
        code = self._combo.itemData(index)
        self._processor.update_config(flip_code=code)
        self.controls_changed.emit()


ProcessorControlsRegistry.register(FlipTransformation, FlipControlWidget)
