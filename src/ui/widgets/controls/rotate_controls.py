from PySide6.QtWidgets import QCheckBox, QFormLayout

from src.processors.spatial.rotate import RotateTransformation
from src.ui.widgets.controls._utils import FloatSliderRow
from src.ui.widgets.processor_controls import BaseProcessorControlWidget, ProcessorControlsRegistry


class RotateControlWidget(BaseProcessorControlWidget):
    def _build_ui(self) -> None:
        layout = QFormLayout(self)
        cfg = self._processor._config

        self._angle = FloatSliderRow(-180.0, 180.0, cfg.angle, decimals=1, scale=10)
        self._scale = FloatSliderRow(0.1, 3.0, cfg.scale, decimals=2, scale=100)
        self._expand = QCheckBox()
        self._expand.setChecked(cfg.expand)

        self._angle.value_changed.connect(lambda v: (self._processor.update_config(angle=v), self.controls_changed.emit()))
        self._scale.value_changed.connect(lambda v: (self._processor.update_config(scale=v), self.controls_changed.emit()))
        self._expand.stateChanged.connect(lambda s: (self._processor.update_config(expand=bool(s)), self.controls_changed.emit()))

        layout.addRow("Angle °", self._angle)
        layout.addRow("Scale", self._scale)
        layout.addRow("Expand canvas", self._expand)


ProcessorControlsRegistry.register(RotateTransformation, RotateControlWidget)
