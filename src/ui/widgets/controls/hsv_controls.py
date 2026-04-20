from PySide6.QtWidgets import QFormLayout

from src.processors.color_transformations.hsv_adjust import HSVAdjustTransformation
from src.ui.widgets.controls._utils import FloatSliderRow
from src.ui.widgets.processor_controls import BaseProcessorControlWidget, ProcessorControlsRegistry


class HSVControlWidget(BaseProcessorControlWidget):
    def _build_ui(self) -> None:
        layout = QFormLayout(self)
        cfg = self._processor._config

        self._hue = FloatSliderRow(-90.0, 90.0, cfg.hue_shift, decimals=1, scale=10)
        self._sat = FloatSliderRow(0.0, 3.0, cfg.saturation_scale, decimals=2, scale=100)
        self._val = FloatSliderRow(0.0, 3.0, cfg.value_scale, decimals=2, scale=100)

        self._hue.value_changed.connect(lambda v: (self._processor.update_config(hue_shift=v), self.controls_changed.emit()))
        self._sat.value_changed.connect(lambda v: (self._processor.update_config(saturation_scale=v), self.controls_changed.emit()))
        self._val.value_changed.connect(lambda v: (self._processor.update_config(value_scale=v), self.controls_changed.emit()))

        layout.addRow("Hue shift", self._hue)
        layout.addRow("Saturation ×", self._sat)
        layout.addRow("Value ×", self._val)


ProcessorControlsRegistry.register(HSVAdjustTransformation, HSVControlWidget)
