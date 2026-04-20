from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDoubleSpinBox, QFormLayout, QSlider

from src.processors.color_transformations.brightness_contrast import BrightnessContrastTransformation
from src.ui.widgets.processor_controls import BaseProcessorControlWidget, ProcessorControlsRegistry


class BrightnessContrastControlWidget(BaseProcessorControlWidget):
    def _build_ui(self) -> None:
        layout = QFormLayout(self)

        # Alpha (contrast): 0.1 – 4.0, stored *10 in slider
        self._alpha_slider = QSlider(Qt.Orientation.Horizontal)
        self._alpha_slider.setRange(1, 400)
        self._alpha_slider.setValue(int(self._processor._config.alpha * 100))

        self._alpha_spin = QDoubleSpinBox()
        self._alpha_spin.setRange(0.01, 4.0)
        self._alpha_spin.setSingleStep(0.01)
        self._alpha_spin.setValue(self._processor._config.alpha)

        # Beta (brightness): -127 – 127
        self._beta_slider = QSlider(Qt.Orientation.Horizontal)
        self._beta_slider.setRange(-127, 127)
        self._beta_slider.setValue(int(self._processor._config.beta))

        self._beta_spin = QDoubleSpinBox()
        self._beta_spin.setRange(-127.0, 127.0)
        self._beta_spin.setSingleStep(1.0)
        self._beta_spin.setValue(self._processor._config.beta)

        self._alpha_slider.valueChanged.connect(self._alpha_slider_changed)
        self._alpha_spin.valueChanged.connect(self._alpha_spin_changed)
        self._beta_slider.valueChanged.connect(self._beta_slider_changed)
        self._beta_spin.valueChanged.connect(self._beta_spin_changed)

        layout.addRow("Contrast (α)", self._alpha_slider)
        layout.addRow("", self._alpha_spin)
        layout.addRow("Brightness (β)", self._beta_slider)
        layout.addRow("", self._beta_spin)

    def _alpha_slider_changed(self, value: int) -> None:
        v = value / 100.0
        self._alpha_spin.blockSignals(True)
        self._alpha_spin.setValue(v)
        self._alpha_spin.blockSignals(False)
        self._processor.update_config(alpha=v)
        self.controls_changed.emit()

    def _alpha_spin_changed(self, value: float) -> None:
        self._alpha_slider.blockSignals(True)
        self._alpha_slider.setValue(int(value * 100))
        self._alpha_slider.blockSignals(False)
        self._processor.update_config(alpha=value)
        self.controls_changed.emit()

    def _beta_slider_changed(self, value: int) -> None:
        self._beta_spin.blockSignals(True)
        self._beta_spin.setValue(float(value))
        self._beta_spin.blockSignals(False)
        self._processor.update_config(beta=float(value))
        self.controls_changed.emit()

    def _beta_spin_changed(self, value: float) -> None:
        self._beta_slider.blockSignals(True)
        self._beta_slider.setValue(int(value))
        self._beta_slider.blockSignals(False)
        self._processor.update_config(beta=value)
        self.controls_changed.emit()


ProcessorControlsRegistry.register(BrightnessContrastTransformation, BrightnessContrastControlWidget)
