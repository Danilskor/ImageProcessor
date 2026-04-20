from PySide6.QtWidgets import QComboBox, QFormLayout

from src.processors.filters.skeleton import SKELETON_METHODS, SkeletonTransformation
from src.ui.widgets.processor_controls import BaseProcessorControlWidget, ProcessorControlsRegistry

_METHOD_LABELS = {
    "zhang_suen": "Zhang-Suen",
    "guo_hall": "Guo-Hall",
    "morphological": "Morphological",
}


class SkeletonControlWidget(BaseProcessorControlWidget):
    def _build_ui(self) -> None:
        layout = QFormLayout(self)
        cfg = self._processor._config

        self._method_combo = QComboBox()
        for key in SKELETON_METHODS:
            self._method_combo.addItem(_METHOD_LABELS[key], userData=key)
        current_idx = SKELETON_METHODS.index(cfg.method)
        self._method_combo.setCurrentIndex(current_idx)

        self._method_combo.currentIndexChanged.connect(self._on_method_changed)
        layout.addRow("Method", self._method_combo)

    def _on_method_changed(self, index: int) -> None:
        method = self._method_combo.itemData(index)
        self._processor.update_config(method=method)
        self.controls_changed.emit()


ProcessorControlsRegistry.register(SkeletonTransformation, SkeletonControlWidget)
