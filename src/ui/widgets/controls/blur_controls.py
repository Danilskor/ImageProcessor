from PySide6.QtCore import Qt
from PySide6.QtWidgets import QComboBox, QFormLayout, QSlider, QLabel, QHBoxLayout, QWidget

from src.processors.filters.blur import BlurTransformation, BLUR_TYPES
from src.ui.widgets.processor_controls import BaseProcessorControlWidget, ProcessorControlsRegistry


class BlurControlWidget(BaseProcessorControlWidget):
    def _build_ui(self) -> None:
        layout = QFormLayout(self)
        cfg = self._processor._config

        # Kernel size: odd values 1..51 → slider index maps to 2*i+1
        self._slider = QSlider(Qt.Orientation.Horizontal)
        self._slider.setRange(0, 25)   # index → kernel = 2*index + 1
        self._slider.setValue((cfg.kernel_size - 1) // 2)

        self._size_label = QLabel(str(cfg.kernel_size))

        row = QWidget()
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.addWidget(self._slider, stretch=1)
        row_layout.addWidget(self._size_label)

        self._type_combo = QComboBox()
        for t in BLUR_TYPES:
            self._type_combo.addItem(t)
        self._type_combo.setCurrentText(cfg.blur_type)

        self._slider.valueChanged.connect(self._kernel_changed)
        self._type_combo.currentTextChanged.connect(self._type_changed)

        layout.addRow("Kernel size", row)
        layout.addRow("Type", self._type_combo)

    def _kernel_changed(self, index: int) -> None:
        k = 2 * index + 1
        self._size_label.setText(str(k))
        self._processor.update_config(kernel_size=k)
        self.controls_changed.emit()

    def _type_changed(self, text: str) -> None:
        self._processor.update_config(blur_type=text)
        self.controls_changed.emit()


ProcessorControlsRegistry.register(BlurTransformation, BlurControlWidget)
