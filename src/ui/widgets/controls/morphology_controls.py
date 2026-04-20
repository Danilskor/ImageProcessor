from PySide6.QtWidgets import QComboBox, QFormLayout, QSpinBox

from src.processors.filters.morphology import MORPH_OPS, MORPH_SHAPES, MorphologyTransformation
from src.ui.widgets.processor_controls import BaseProcessorControlWidget, ProcessorControlsRegistry

_OP_LABELS = {
    "erode":    "Erosion",
    "dilate":   "Dilation",
    "open":     "Opening",
    "close":    "Closing",
    "gradient": "Gradient",
    "tophat":   "Top-hat",
    "blackhat": "Black-hat",
}

_SHAPE_LABELS = {
    "rect":    "Rectangle",
    "ellipse": "Ellipse",
    "cross":   "Cross",
}


class MorphologyControlWidget(BaseProcessorControlWidget):
    def _build_ui(self) -> None:
        layout = QFormLayout(self)
        cfg = self._processor._config

        self._op_combo = QComboBox()
        for key in MORPH_OPS:
            self._op_combo.addItem(_OP_LABELS[key], userData=key)
        self._op_combo.setCurrentIndex(list(MORPH_OPS).index(cfg.operation))

        self._shape_combo = QComboBox()
        for key in MORPH_SHAPES:
            self._shape_combo.addItem(_SHAPE_LABELS[key], userData=key)
        self._shape_combo.setCurrentIndex(list(MORPH_SHAPES).index(cfg.kernel_shape))

        self._size_spin = QSpinBox()
        self._size_spin.setRange(1, 99)
        self._size_spin.setSingleStep(2)
        self._size_spin.setValue(cfg.kernel_size)

        self._iter_spin = QSpinBox()
        self._iter_spin.setRange(1, 20)
        self._iter_spin.setValue(cfg.iterations)

        self._op_combo.currentIndexChanged.connect(
            lambda i: self._update(operation=self._op_combo.itemData(i))
        )
        self._shape_combo.currentIndexChanged.connect(
            lambda i: self._update(kernel_shape=self._shape_combo.itemData(i))
        )
        self._size_spin.valueChanged.connect(lambda v: self._update(kernel_size=v))
        self._iter_spin.valueChanged.connect(lambda v: self._update(iterations=v))

        layout.addRow("Operation", self._op_combo)
        layout.addRow("Kernel shape", self._shape_combo)
        layout.addRow("Kernel size", self._size_spin)
        layout.addRow("Iterations", self._iter_spin)

    def _update(self, **kwargs) -> None:
        self._processor.update_config(**kwargs)
        self.controls_changed.emit()


ProcessorControlsRegistry.register(MorphologyTransformation, MorphologyControlWidget)
