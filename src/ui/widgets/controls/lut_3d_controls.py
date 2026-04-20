from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFileDialog,
    QFormLayout,
    QLabel,
    QPushButton,
    QSlider,
)

from src.processors.lut.lut_3d import LUT3DTransformation
from src.ui.widgets.processor_controls import BaseProcessorControlWidget, ProcessorControlsRegistry


class LUT3DControlWidget(BaseProcessorControlWidget):
    def _build_ui(self) -> None:
        layout = QFormLayout(self)

        self._file_label = QLabel(self._processor._config.cube_path or "(no file loaded)")
        self._file_label.setWordWrap(True)

        load_btn = QPushButton("Load .cube file…")
        load_btn.clicked.connect(self._load_file)

        self._strength_slider = QSlider(Qt.Orientation.Horizontal)
        self._strength_slider.setRange(0, 100)
        self._strength_slider.setValue(int(self._processor._config.strength * 100))
        self._strength_slider.valueChanged.connect(self._strength_changed)

        self._strength_label = QLabel(f"{self._processor._config.strength:.0%}")

        layout.addRow("File", self._file_label)
        layout.addRow("", load_btn)
        layout.addRow("Strength", self._strength_slider)
        layout.addRow("", self._strength_label)

    def _load_file(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Open LUT file", "", "CUBE Files (*.cube)"
        )
        if path:
            self._processor.update_config(cube_path=path)
            self._file_label.setText(path)
            self.controls_changed.emit()

    def _strength_changed(self, value: int) -> None:
        strength = value / 100.0
        self._strength_label.setText(f"{strength:.0%}")
        self._processor.update_config(strength=strength)
        self.controls_changed.emit()


ProcessorControlsRegistry.register(LUT3DTransformation, LUT3DControlWidget)
