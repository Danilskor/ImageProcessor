from PySide6.QtWidgets import QDoubleSpinBox, QFormLayout, QSlider
from PySide6.QtCore import Qt

from src.processors.color_transformations.gamma import GammaTransformation
from src.ui.widgets.processor_controls import BaseProcessorControlWidget, ProcessorControlsRegistry


class GammaControlWidget(BaseProcessorControlWidget):
    def _build_ui(self) -> None:
        layout = QFormLayout(self)

        self._slider = QSlider(Qt.Orientation.Horizontal)
        self._slider.setRange(1, 300)
        self._slider.setValue(int(self._processor._config.gamma * 100))

        self._spin = QDoubleSpinBox()
        self._spin.setRange(0.01, 3.0)
        self._spin.setSingleStep(0.01)
        self._spin.setValue(self._processor._config.gamma)

        self._slider.valueChanged.connect(self._slider_changed)
        self._spin.valueChanged.connect(self._spin_changed)

        layout.addRow("Gamma", self._slider)
        layout.addRow("", self._spin)

    def _slider_changed(self, value: int) -> None:
        gamma = value / 100.0
        self._spin.blockSignals(True)
        self._spin.setValue(gamma)
        self._spin.blockSignals(False)
        self._processor.update_config(gamma=gamma)
        self.controls_changed.emit()

    def _spin_changed(self, value: float) -> None:
        self._slider.blockSignals(True)
        self._slider.setValue(int(value * 100))
        self._slider.blockSignals(False)
        self._processor.update_config(gamma=value)
        self.controls_changed.emit()


ProcessorControlsRegistry.register(GammaTransformation, GammaControlWidget)
