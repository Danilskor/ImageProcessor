from PySide6.QtWidgets import QComboBox, QFormLayout

from src.processors.filters.edge_detect import EdgeDetectTransformation, EDGE_METHODS
from src.ui.widgets.controls._utils import FloatSliderRow
from src.ui.widgets.processor_controls import BaseProcessorControlWidget, ProcessorControlsRegistry


class EdgeDetectControlWidget(BaseProcessorControlWidget):
    def _build_ui(self) -> None:
        layout = QFormLayout(self)
        cfg = self._processor._config

        self._method_combo = QComboBox()
        for m in EDGE_METHODS:
            self._method_combo.addItem(m)
        self._method_combo.setCurrentText(cfg.method)

        self._t1 = FloatSliderRow(0.0, 500.0, cfg.threshold1, decimals=0, scale=1)
        self._t2 = FloatSliderRow(0.0, 500.0, cfg.threshold2, decimals=0, scale=1)

        self._method_combo.currentTextChanged.connect(self._method_changed)
        self._t1.value_changed.connect(lambda v: (self._processor.update_config(threshold1=v), self.controls_changed.emit()))
        self._t2.value_changed.connect(lambda v: (self._processor.update_config(threshold2=v), self.controls_changed.emit()))

        layout.addRow("Method", self._method_combo)
        layout.addRow("Threshold 1", self._t1)
        layout.addRow("Threshold 2", self._t2)

    def _method_changed(self, text: str) -> None:
        self._processor.update_config(method=text)
        self.controls_changed.emit()


ProcessorControlsRegistry.register(EdgeDetectTransformation, EdgeDetectControlWidget)
