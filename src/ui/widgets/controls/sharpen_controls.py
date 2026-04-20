from PySide6.QtWidgets import QFormLayout

from src.processors.filters.sharpen import SharpenTransformation
from src.ui.widgets.controls._utils import FloatSliderRow
from src.ui.widgets.processor_controls import BaseProcessorControlWidget, ProcessorControlsRegistry


class SharpenControlWidget(BaseProcessorControlWidget):
    def _build_ui(self) -> None:
        layout = QFormLayout(self)
        cfg = self._processor._config

        self._strength = FloatSliderRow(0.0, 5.0, cfg.strength, decimals=2, scale=100)
        self._strength.value_changed.connect(
            lambda v: (self._processor.update_config(strength=v), self.controls_changed.emit())
        )

        layout.addRow("Strength", self._strength)


ProcessorControlsRegistry.register(SharpenTransformation, SharpenControlWidget)
