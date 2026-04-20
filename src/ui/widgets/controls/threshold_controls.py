from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QSlider,
    QSpinBox,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from src.processors.filters.threshold import (
    ADAPTIVE_METHODS,
    MODES,
    SIMPLE_TYPES,
    ThresholdTransformation,
)
from src.ui.widgets.controls._utils import FloatSliderRow
from src.ui.widgets.processor_controls import BaseProcessorControlWidget, ProcessorControlsRegistry


class ThresholdControlWidget(BaseProcessorControlWidget):
    def _build_ui(self) -> None:
        cfg = self._processor._config
        outer = QVBoxLayout(self)

        # Mode selector
        mode_form = QFormLayout()
        self._mode_combo = QComboBox()
        for m in MODES:
            self._mode_combo.addItem(m.capitalize(), userData=m)
        self._mode_combo.setCurrentText(cfg.mode.capitalize())
        mode_form.addRow("Mode", self._mode_combo)
        outer.addLayout(mode_form)

        # Threshold type (shared by simple + otsu)
        type_form = QFormLayout()
        self._type_combo = QComboBox()
        for name in SIMPLE_TYPES:
            self._type_combo.addItem(name)
        self._type_combo.setCurrentText(cfg.thresh_type)
        type_form.addRow("Type", self._type_combo)
        outer.addLayout(type_form)

        # Stacked param groups: simple | otsu | adaptive
        self._stack = QStackedWidget()

        # ── Simple page ──
        simple_box = QGroupBox()
        sf = QFormLayout(simple_box)
        self._threshold_row = FloatSliderRow(0.0, 255.0, cfg.threshold, decimals=0, scale=1)
        self._maxval_row = FloatSliderRow(0.0, 255.0, cfg.max_val, decimals=0, scale=1)
        sf.addRow("Threshold", self._threshold_row)
        sf.addRow("Max value", self._maxval_row)
        self._stack.addWidget(simple_box)   # index 0 = simple

        # ── Otsu page ──
        otsu_box = QGroupBox()
        of = QFormLayout(otsu_box)
        self._otsu_maxval = FloatSliderRow(0.0, 255.0, cfg.max_val, decimals=0, scale=1)
        of.addRow("Max value", self._otsu_maxval)
        self._stack.addWidget(otsu_box)     # index 1 = otsu

        # ── Adaptive page ──
        adap_box = QGroupBox()
        af = QFormLayout(adap_box)
        self._adap_method = QComboBox()
        for name in ADAPTIVE_METHODS:
            self._adap_method.addItem(name)
        self._adap_method.setCurrentText(cfg.adaptive_method)
        self._adap_maxval = FloatSliderRow(0.0, 255.0, cfg.max_val, decimals=0, scale=1)
        self._block_spin = QSpinBox()
        self._block_spin.setRange(3, 999)
        self._block_spin.setSingleStep(2)
        self._block_spin.setValue(cfg.block_size)
        self._C_spin = QDoubleSpinBox()
        self._C_spin.setRange(-50.0, 50.0)
        self._C_spin.setSingleStep(0.5)
        self._C_spin.setValue(cfg.C)
        af.addRow("Method", self._adap_method)
        af.addRow("Max value", self._adap_maxval)
        af.addRow("Block size", self._block_spin)
        af.addRow("C", self._C_spin)
        self._stack.addWidget(adap_box)     # index 2 = adaptive

        outer.addWidget(self._stack)

        # Set initial page
        self._mode_combo.currentIndexChanged.connect(self._mode_changed)
        self._mode_changed(self._mode_combo.currentIndex())

        # Wire signals
        self._type_combo.currentTextChanged.connect(self._emit("thresh_type"))
        self._threshold_row.value_changed.connect(self._emit_float("threshold"))
        self._maxval_row.value_changed.connect(self._emit_float("max_val"))
        self._otsu_maxval.value_changed.connect(self._emit_float("max_val"))
        self._adap_maxval.value_changed.connect(self._emit_float("max_val"))
        self._adap_method.currentTextChanged.connect(self._emit("adaptive_method"))
        self._block_spin.valueChanged.connect(self._block_changed)
        self._C_spin.valueChanged.connect(lambda v: (self._processor.update_config(C=v), self.controls_changed.emit()))

    # helpers to keep lambdas concise
    def _emit(self, key: str):
        def _slot(val):
            self._processor.update_config(**{key: val})
            self.controls_changed.emit()
        return _slot

    def _emit_float(self, key: str):
        def _slot(val: float):
            self._processor.update_config(**{key: val})
            self.controls_changed.emit()
        return _slot

    def _mode_changed(self, index: int) -> None:
        page = {"simple": 0, "otsu": 1, "adaptive": 2}
        mode = self._mode_combo.itemData(index)
        self._stack.setCurrentIndex(page.get(mode, 0))
        self._processor.update_config(mode=mode)
        self.controls_changed.emit()

    def _block_changed(self, val: int) -> None:
        # enforce odd
        if val % 2 == 0:
            val += 1
            self._block_spin.blockSignals(True)
            self._block_spin.setValue(val)
            self._block_spin.blockSignals(False)
        self._processor.update_config(block_size=val)
        self.controls_changed.emit()


ProcessorControlsRegistry.register(ThresholdTransformation, ThresholdControlWidget)
