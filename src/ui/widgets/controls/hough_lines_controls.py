import numpy as np
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QGroupBox,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSpinBox,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from src.processors.filters.hough_lines import HOUGH_MODES, HoughLinesTransformation
from src.ui.widgets.controls._utils import FloatSliderRow
from src.ui.widgets.processor_controls import BaseProcessorControlWidget, ProcessorControlsRegistry

_HOUGH_SPACE_MAX_W = 360   # display width for Hough space preview

_VIEW_MODES = [
    ("Result (lines overlay)", "result"),
    ("Input edge map", "edges"),
    ("Hough space", "hough"),
]


class HoughLinesControlWidget(BaseProcessorControlWidget):
    """Controls for Hough line detection.

    Exposes on_image_processed(image) so MainWindow can call it after each
    pipeline run to refresh the Hough space and edge visualisations.

    view_override emits the image that should be shown in the main viewer
    (np.ndarray), or None to revert to the normal pipeline result.
    """

    view_override = Signal(object)   # np.ndarray | None

    def _build_ui(self) -> None:
        cfg = self._processor._config
        outer = QVBoxLayout(self)
        outer.setSpacing(6)

        # ── Viewer display mode ───────────────────────────────────────────────
        view_form = QFormLayout()
        self._view_combo = QComboBox()
        for label, key in _VIEW_MODES:
            self._view_combo.addItem(label, userData=key)
        view_form.addRow("Show in viewer", self._view_combo)
        outer.addLayout(view_form)

        # ── Mode ──────────────────────────────────────────────────────────────
        mode_form = QFormLayout()
        self._mode_combo = QComboBox()
        for m in HOUGH_MODES:
            self._mode_combo.addItem(m.capitalize(), userData=m)
        self._mode_combo.setCurrentText(cfg.mode.capitalize())
        mode_form.addRow("Mode", self._mode_combo)
        outer.addLayout(mode_form)

        # ── Common Hough params ───────────────────────────────────────────────
        common_box = QGroupBox("Hough transform")
        hf = QFormLayout(common_box)
        self._rho = FloatSliderRow(0.5, 10.0, cfg.rho, decimals=1, scale=10)
        self._theta = FloatSliderRow(0.1, 5.0, cfg.theta_deg, decimals=1, scale=10)
        self._thresh = FloatSliderRow(1, 1000, cfg.threshold, decimals=0, scale=1)
        hf.addRow("ρ resolution (px)", self._rho)
        hf.addRow("θ resolution (°)", self._theta)
        hf.addRow("Vote threshold", self._thresh)
        outer.addWidget(common_box)

        # ── Probabilistic-only params ─────────────────────────────────────────
        self._prob_box = QGroupBox("Probabilistic params")
        pf = QFormLayout(self._prob_box)
        self._min_len = FloatSliderRow(0.0, 500.0, cfg.min_line_length, decimals=0, scale=1)
        self._max_gap = FloatSliderRow(0.0, 200.0, cfg.max_line_gap, decimals=0, scale=1)
        pf.addRow("Min line length", self._min_len)
        pf.addRow("Max line gap", self._max_gap)
        outer.addWidget(self._prob_box)

        # ── Line style ────────────────────────────────────────────────────────
        style_box = QGroupBox("Line style")
        sf = QFormLayout(style_box)
        self._thickness_spin = QSpinBox()
        self._thickness_spin.setRange(1, 20)
        self._thickness_spin.setValue(cfg.line_thickness)
        sf.addRow("Thickness", self._thickness_spin)
        outer.addWidget(style_box)

        # ── Info label ────────────────────────────────────────────────────────
        self._info_label = QLabel("Lines detected: —")
        outer.addWidget(self._info_label)

        # ── Hough space visualisation ─────────────────────────────────────────
        vis_box = QGroupBox("Hough space  (ρ ↕  θ →  0…180°)")
        vis_layout = QVBoxLayout(vis_box)

        self._hough_label = QLabel("Run pipeline to see Hough space.")
        self._hough_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._hough_label.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
        )

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self._hough_label)
        scroll.setMinimumHeight(180)
        vis_layout.addWidget(scroll)

        # ── Edge image ────────────────────────────────────────────────────────
        edge_box = QGroupBox("Input edge image")
        edge_layout = QVBoxLayout(edge_box)
        self._edge_label = QLabel("Run pipeline to see edges.")
        self._edge_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._edge_label.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
        )
        edge_scroll = QScrollArea()
        edge_scroll.setWidgetResizable(True)
        edge_scroll.setWidget(self._edge_label)
        edge_scroll.setMinimumHeight(120)
        edge_layout.addWidget(edge_scroll)

        outer.addWidget(vis_box)
        outer.addWidget(edge_box)

        # ── Wire signals ──────────────────────────────────────────────────────
        self._view_combo.currentIndexChanged.connect(self._view_mode_changed)

        self._mode_combo.currentIndexChanged.connect(self._mode_changed)
        self._mode_changed(self._mode_combo.currentIndex())

        self._rho.value_changed.connect(lambda v: self._update("rho", v))
        self._theta.value_changed.connect(lambda v: self._update("theta_deg", v))
        self._thresh.value_changed.connect(lambda v: self._update("threshold", int(v)))
        self._min_len.value_changed.connect(lambda v: self._update("min_line_length", v))
        self._max_gap.value_changed.connect(lambda v: self._update("max_line_gap", v))
        self._thickness_spin.valueChanged.connect(lambda v: self._update("line_thickness", v))

    # ── Slots ─────────────────────────────────────────────────────────────────

    def _mode_changed(self, index: int) -> None:
        mode = self._mode_combo.itemData(index)
        self._prob_box.setVisible(mode == "probabilistic")
        self._processor.update_config(mode=mode)
        self.controls_changed.emit()

    def _update(self, key: str, value) -> None:
        self._processor.update_config(**{key: value})
        self.controls_changed.emit()

    def _view_mode_changed(self) -> None:
        self._emit_view_override()

    def _emit_view_override(self) -> None:
        mode = self._view_combo.currentData()
        proc: HoughLinesTransformation = self._processor
        if mode == "edges" and proc.edge_image is not None:
            self.view_override.emit(proc.edge_image)
        elif mode == "hough" and proc.hough_space_image is not None:
            self.view_override.emit(proc.hough_space_image)
        else:
            self.view_override.emit(None)

    @Slot(object)
    def on_image_processed(self, _image: np.ndarray) -> None:
        """Called by MainWindow after each pipeline run to refresh visualisations."""
        proc: HoughLinesTransformation = self._processor
        self._info_label.setText(f"Lines detected: {proc.lines_count}")

        if proc.hough_space_image is not None:
            self._set_label_image(self._hough_label, proc.hough_space_image)

        if proc.edge_image is not None:
            self._set_label_image(self._edge_label, proc.edge_image)

        if proc.hough_space_max_votes > 0:
            cur = self._thresh.value()
            self._thresh.set_range(1, proc.hough_space_max_votes)
            # Clamp current value to new range
            self._thresh.set_value(min(cur, proc.hough_space_max_votes))

        self._emit_view_override()

    # ── Helpers ───────────────────────────────────────────────────────────────

    @staticmethod
    def _set_label_image(label: QLabel, image: np.ndarray) -> None:
        """Scale image to fit label width and display it."""
        h, w = image.shape[:2]
        display_w = min(w, _HOUGH_SPACE_MAX_W)
        display_h = int(h * display_w / w)
        small = image if display_w == w else __import__("cv2").resize(
            image, (display_w, display_h)
        )
        stride = small.strides[0]
        q_img = QImage(
            small.tobytes(),
            small.shape[1], small.shape[0],
            stride,
            QImage.Format.Format_BGR888,
        )
        label.setPixmap(QPixmap.fromImage(q_img))
        label.resize(q_img.size())


ProcessorControlsRegistry.register(HoughLinesTransformation, HoughLinesControlWidget)
