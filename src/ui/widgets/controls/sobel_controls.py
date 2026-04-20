from PySide6.QtWidgets import QComboBox, QFormLayout, QSpinBox

from src.processors.filters.sobel import SOBEL_DIRECTIONS, VALID_KSIZES, SobelTransformation
from src.ui.widgets.controls._utils import FloatSliderRow
from src.ui.widgets.processor_controls import BaseProcessorControlWidget, ProcessorControlsRegistry


class SobelControlWidget(BaseProcessorControlWidget):
    def _build_ui(self) -> None:
        layout = QFormLayout(self)
        cfg = self._processor._config

        self._dir_combo = QComboBox()
        for d in SOBEL_DIRECTIONS:
            self._dir_combo.addItem(d.capitalize(), userData=d)
        self._dir_combo.setCurrentText(cfg.direction.capitalize())

        self._ksize_combo = QComboBox()
        for k in VALID_KSIZES:
            self._ksize_combo.addItem(str(k), userData=k)
        self._ksize_combo.setCurrentText(str(cfg.ksize))

        self._scale = FloatSliderRow(0.1, 5.0, cfg.scale, decimals=2, scale=100)
        self._delta = FloatSliderRow(-128.0, 128.0, cfg.delta, decimals=0, scale=1)

        self._dir_combo.currentIndexChanged.connect(self._dir_changed)
        self._ksize_combo.currentIndexChanged.connect(self._ksize_changed)
        self._scale.value_changed.connect(lambda v: (self._processor.update_config(scale=v), self.controls_changed.emit()))
        self._delta.value_changed.connect(lambda v: (self._processor.update_config(delta=v), self.controls_changed.emit()))

        layout.addRow("Direction", self._dir_combo)
        layout.addRow("Kernel size", self._ksize_combo)
        layout.addRow("Scale", self._scale)
        layout.addRow("Delta", self._delta)

    def _dir_changed(self, index: int) -> None:
        self._processor.update_config(direction=self._dir_combo.itemData(index))
        self.controls_changed.emit()

    def _ksize_changed(self, index: int) -> None:
        self._processor.update_config(ksize=self._ksize_combo.itemData(index))
        self.controls_changed.emit()


ProcessorControlsRegistry.register(SobelTransformation, SobelControlWidget)
