from PySide6.QtWidgets import QFormLayout

from src.processors.color_transformations.white_balance import WhiteBalanceTransformation
from src.ui.widgets.controls._utils import FloatSliderRow
from src.ui.widgets.processor_controls import BaseProcessorControlWidget, ProcessorControlsRegistry


class WhiteBalanceControlWidget(BaseProcessorControlWidget):
    def _build_ui(self) -> None:
        layout = QFormLayout(self)
        cfg = self._processor._config

        self._r = FloatSliderRow(0.0, 3.0, cfg.r_gain, decimals=2, scale=100)
        self._g = FloatSliderRow(0.0, 3.0, cfg.g_gain, decimals=2, scale=100)
        self._b = FloatSliderRow(0.0, 3.0, cfg.b_gain, decimals=2, scale=100)

        self._r.value_changed.connect(lambda v: (self._processor.update_config(r_gain=v), self.controls_changed.emit()))
        self._g.value_changed.connect(lambda v: (self._processor.update_config(g_gain=v), self.controls_changed.emit()))
        self._b.value_changed.connect(lambda v: (self._processor.update_config(b_gain=v), self.controls_changed.emit()))

        layout.addRow("R gain", self._r)
        layout.addRow("G gain", self._g)
        layout.addRow("B gain", self._b)


ProcessorControlsRegistry.register(WhiteBalanceTransformation, WhiteBalanceControlWidget)
