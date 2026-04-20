from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget

from src.base.base_processor import BaseProcessor


class BaseProcessorControlWidget(QWidget):
    controls_changed = Signal()

    def __init__(self, processor: BaseProcessor, parent=None):
        super().__init__(parent)
        self._processor = processor
        self._build_ui()

    def _build_ui(self) -> None:
        raise NotImplementedError


class ProcessorControlsRegistry:
    _registry: dict[type, type[BaseProcessorControlWidget]] = {}

    @classmethod
    def register(cls, processor_type: type, widget_type: type[BaseProcessorControlWidget]) -> None:
        cls._registry[processor_type] = widget_type

    @classmethod
    def get_widget(
        cls, processor: BaseProcessor, parent=None
    ) -> BaseProcessorControlWidget | None:
        widget_type = cls._registry.get(type(processor))
        if widget_type is None:
            return None
        return widget_type(processor, parent)
