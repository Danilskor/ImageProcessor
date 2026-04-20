from PySide6.QtWidgets import QFormLayout, QLabel

from src.processors.color_transformations.grayscale import GrayscaleTransformation
from src.ui.widgets.processor_controls import BaseProcessorControlWidget, ProcessorControlsRegistry


class GrayscaleControlWidget(BaseProcessorControlWidget):
    def _build_ui(self) -> None:
        layout = QFormLayout(self)
        layout.addRow(QLabel("No parameters."))


ProcessorControlsRegistry.register(GrayscaleTransformation, GrayscaleControlWidget)
