from PySide6.QtWidgets import QFormLayout

from src.processors.color_transformations.saturation import SaturationTransformation
from src.ui.widgets.controls._utils import FloatSliderRow
from src.ui.widgets.processor_controls import BaseProcessorControlWidget, ProcessorControlsRegistry


class SaturationControlWidget(BaseProcessorControlWidget):
    def _build_ui(self) -> None:
        layout = QFormLayout(self)
        cfg = self._processor._config

        self._scale = FloatSliderRow(0.0, 4.0, cfg.scale, decimals=2, scale=100)
        self._scale.value_changed.connect(
            lambda v: (self._processor.update_config(scale=v), self.controls_changed.emit())
        )

        layout.addRow("Saturation ×", self._scale)


ProcessorControlsRegistry.register(SaturationTransformation, SaturationControlWidget)
