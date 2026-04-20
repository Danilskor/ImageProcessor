from PySide6.QtWidgets import QFormLayout

from src.processors.tone.exposure import ExposureTransformation
from src.ui.widgets.controls._utils import FloatSliderRow
from src.ui.widgets.processor_controls import BaseProcessorControlWidget, ProcessorControlsRegistry


class ExposureControlWidget(BaseProcessorControlWidget):
    def _build_ui(self) -> None:
        layout = QFormLayout(self)
        cfg = self._processor._config

        self._ev = FloatSliderRow(-5.0, 5.0, cfg.ev_stops, decimals=2, scale=100)
        self._ev.value_changed.connect(
            lambda v: (self._processor.update_config(ev_stops=v), self.controls_changed.emit())
        )

        layout.addRow("EV stops", self._ev)


ProcessorControlsRegistry.register(ExposureTransformation, ExposureControlWidget)
