from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QDockWidget,
    QFileDialog,
    QMainWindow,
    QMenu,
    QMessageBox,
    QScrollArea,
    QToolBar,
    QWidget,
)
from PySide6.QtGui import QAction

from src.pipeline import ProcessingPipeline
from src.processors.color_transformations.gamma import GammaTransformation
from src.processors.color_transformations.brightness_contrast import BrightnessContrastTransformation
from src.processors.color_transformations.hsv_adjust import HSVAdjustTransformation
from src.processors.color_transformations.white_balance import WhiteBalanceTransformation
from src.processors.color_transformations.saturation import SaturationTransformation
from src.processors.color_transformations.grayscale import GrayscaleTransformation
from src.processors.filters.blur import BlurTransformation
from src.processors.filters.sharpen import SharpenTransformation
from src.processors.filters.sobel import SobelTransformation
from src.processors.filters.edge_detect import EdgeDetectTransformation
from src.processors.filters.threshold import ThresholdTransformation
from src.processors.filters.hough_lines import HoughLinesTransformation
from src.processors.filters.morphology import MorphologyTransformation
from src.processors.filters.skeleton import SkeletonTransformation
from src.processors.spatial.resize import ResizeTransformation
from src.processors.spatial.crop import CropTransformation
from src.processors.spatial.rotate import RotateTransformation
from src.processors.spatial.flip import FlipTransformation
from src.processors.tone.exposure import ExposureTransformation
from src.processors.lut.lut_3d import LUT3DTransformation
from src.ui.app_controller import AppController
from src.ui import theme as _theme
from src.ui.theme import Theme
from src.ui.widgets.histogram import HistogramWidget
from src.ui.widgets.image_viewer import ImageViewerWidget
from src.ui.widgets.layers_panel import LayersPanelWidget
from src.ui.widgets.pipeline_panel import PipelinePanel
from src.ui.widgets.processor_controls import ProcessorControlsRegistry

# Register all control widgets by importing the modules
import src.ui.widgets.controls.gamma_controls  # noqa: F401
import src.ui.widgets.controls.brightness_contrast_controls  # noqa: F401
import src.ui.widgets.controls.hsv_controls  # noqa: F401
import src.ui.widgets.controls.white_balance_controls  # noqa: F401
import src.ui.widgets.controls.blur_controls  # noqa: F401
import src.ui.widgets.controls.sharpen_controls  # noqa: F401
import src.ui.widgets.controls.sobel_controls  # noqa: F401
import src.ui.widgets.controls.edge_detect_controls  # noqa: F401
import src.ui.widgets.controls.rotate_controls  # noqa: F401
import src.ui.widgets.controls.flip_controls  # noqa: F401
import src.ui.widgets.controls.resize_controls  # noqa: F401
import src.ui.widgets.controls.crop_controls  # noqa: F401
import src.ui.widgets.controls.exposure_controls  # noqa: F401
import src.ui.widgets.controls.lut_3d_controls  # noqa: F401
import src.ui.widgets.controls.saturation_controls  # noqa: F401
import src.ui.widgets.controls.grayscale_controls  # noqa: F401
import src.ui.widgets.controls.threshold_controls  # noqa: F401
import src.ui.widgets.controls.hough_lines_controls  # noqa: F401
import src.ui.widgets.controls.morphology_controls  # noqa: F401
import src.ui.widgets.controls.skeleton_controls  # noqa: F401

_ADD_STEP_MENU: dict[str, list[tuple[str, type]]] = {
    "Color": [
        ("Gamma", GammaTransformation),
        ("Brightness / Contrast", BrightnessContrastTransformation),
        ("Saturation", SaturationTransformation),
        ("HSV Adjust", HSVAdjustTransformation),
        ("White Balance", WhiteBalanceTransformation),
        ("Grayscale", GrayscaleTransformation),
    ],
    "LUT": [
        ("3D LUT (.cube)", LUT3DTransformation),
    ],
    "Filters": [
        ("Blur", BlurTransformation),
        ("Sharpen", SharpenTransformation),
        ("Sobel", SobelTransformation),
        ("Edge Detect", EdgeDetectTransformation),
        ("Threshold / Binarize", ThresholdTransformation),
        ("Hough Lines", HoughLinesTransformation),
        ("Morphology", MorphologyTransformation),
        ("Skeleton / Thinning", SkeletonTransformation),
    ],
    "Spatial": [
        ("Resize", ResizeTransformation),
        ("Crop", CropTransformation),
        ("Rotate", RotateTransformation),
        ("Flip", FlipTransformation),
    ],
    "Tone": [
        ("Exposure", ExposureTransformation),
    ],
}


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ImageProcessor")
        self.resize(1280, 800)

        self._pipeline = ProcessingPipeline()
        self._controller = AppController(self._pipeline, parent=self)
        self._controller.image_processed.connect(self._on_image_processed)
        self._controller.thumbnails_ready.connect(self._on_thumbnails_ready)

        self._crop_step_name: str | None = None      # name of active crop step (or None)
        self._last_processed: object = None           # last result from pipeline
        self._viewing_step: str | None = None         # layer selected in layers panel
        self._hough_override_widget = None            # widget that owns view_override signal

        self._build_central()
        self._build_docks()
        self._build_menu()
        self._build_toolbar()

    # ── Central widget ────────────────────────────────────────────────────────

    def _build_central(self) -> None:
        self._viewer = ImageViewerWidget()
        self.setCentralWidget(self._viewer)

    # ── Dock widgets ──────────────────────────────────────────────────────────

    def _build_docks(self) -> None:
        # Left dock: pipeline
        self._pipeline_panel = PipelinePanel(
            self._pipeline, add_menu_spec=_ADD_STEP_MENU
        )
        self._pipeline_panel.step_selected.connect(self._show_controls_for)
        self._pipeline_panel.step_toggled.connect(lambda *_: self._controller.request_update())
        self._pipeline_panel.step_remove_requested.connect(
            lambda *_: self._controller.request_update()
        )
        self._pipeline_panel.order_changed.connect(self._controller.request_update)
        self._pipeline_panel.add_step_requested.connect(self._add_step)

        left_dock = QDockWidget("Pipeline", self)
        left_dock.setWidget(self._pipeline_panel)
        left_dock.setMinimumWidth(220)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, left_dock)

        # Left dock (tabbed): layers panel
        self._layers_panel = LayersPanelWidget()
        self._layers_panel.layer_view_requested.connect(self._on_layer_view_requested)
        layers_dock = QDockWidget("Layers", self)
        layers_dock.setWidget(self._layers_panel)
        layers_dock.setMinimumWidth(160)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, layers_dock)
        self.tabifyDockWidget(left_dock, layers_dock)

        # Right dock: processor controls in a scroll area
        self._controls_container: QWidget | None = None
        self._controls_scroll = QScrollArea()
        self._controls_scroll.setWidgetResizable(True)
        self._controls_scroll.setWidget(QWidget())
        right_dock = QDockWidget("Controls", self)
        right_dock.setWidget(self._controls_scroll)
        right_dock.setMinimumWidth(280)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, right_dock)
        self._right_dock = right_dock

        # Bottom dock: histogram
        self._histogram = HistogramWidget()
        bottom_dock = QDockWidget("Histogram", self)
        bottom_dock.setWidget(self._histogram)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, bottom_dock)

    # ── Menu ──────────────────────────────────────────────────────────────────

    def _build_menu(self) -> None:
        menubar = self.menuBar()

        file_menu = menubar.addMenu("File")
        open_act = QAction("Open image…", self)
        open_act.setShortcut("Ctrl+O")
        open_act.triggered.connect(self._open_image)
        save_act = QAction("Save result…", self)
        save_act.setShortcut("Ctrl+S")
        save_act.triggered.connect(self._save_image)
        file_menu.addAction(open_act)
        file_menu.addAction(save_act)

        file_menu.addSeparator()
        open_proj_act = QAction("Open project…", self)
        open_proj_act.setShortcut("Ctrl+Shift+O")
        open_proj_act.triggered.connect(self._open_project)
        save_proj_act = QAction("Save project…", self)
        save_proj_act.setShortcut("Ctrl+Shift+S")
        save_proj_act.triggered.connect(self._save_project)
        file_menu.addAction(open_proj_act)
        file_menu.addAction(save_proj_act)

        pipeline_menu = menubar.addMenu("Pipeline")
        add_menu = QMenu("Add step", self)
        for category, entries in _ADD_STEP_MENU.items():
            cat_menu = QMenu(category, self)
            for label, processor_cls in entries:
                act = QAction(label, self)
                act.triggered.connect(
                    lambda checked=False, lbl=label, cls=processor_cls: self._add_step(lbl, cls)
                )
                cat_menu.addAction(act)
            add_menu.addMenu(cat_menu)
        pipeline_menu.addMenu(add_menu)

        view_menu = menubar.addMenu("View")
        self._theme_act = QAction("Switch to Light theme", self)
        self._theme_act.setShortcut("Ctrl+T")
        self._theme_act.triggered.connect(self._toggle_theme)
        view_menu.addAction(self._theme_act)

    # ── Toolbar ───────────────────────────────────────────────────────────────

    def _build_toolbar(self) -> None:
        tb = QToolBar("Main", self)
        self.addToolBar(tb)

        open_act = QAction("Open", self)
        open_act.triggered.connect(self._open_image)
        tb.addAction(open_act)

        save_act = QAction("Save", self)
        save_act.triggered.connect(self._save_image)
        tb.addAction(save_act)

        tb.addSeparator()

        fit_act = QAction("Fit", self)
        fit_act.triggered.connect(self._viewer.fit_in_view)
        tb.addAction(fit_act)

        tb.addSeparator()

        theme_act = QAction("☀ / ☾", self)
        theme_act.setToolTip("Toggle dark / light theme  (Ctrl+T)")
        theme_act.triggered.connect(self._toggle_theme)
        tb.addAction(theme_act)

    # ── Slots ─────────────────────────────────────────────────────────────────

    def _open_image(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Open image", "",
            "Images (*.png *.jpg *.jpeg *.bmp *.tiff *.tif *.webp)",
        )
        if path:
            self._controller.load_image(path)

    def _save_image(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self, "Save result", "", "PNG (*.png);;JPEG (*.jpg);;BMP (*.bmp)"
        )
        if path:
            self._controller.save_image(path)

    def _add_step(self, label: str, processor_cls: type) -> None:
        base = label
        n = 1
        name = base
        existing = {s.name for s in self._pipeline.steps}
        while name in existing:
            n += 1
            name = f"{base} {n}"
        self._pipeline.add_step(name, processor_cls())
        self._pipeline_panel.refresh()
        self._controller.request_update()

    def _toggle_theme(self) -> None:
        app = QApplication.instance()
        new = _theme.toggle_theme(app)
        self._theme_act.setText(
            "Switch to Light theme" if new == Theme.DARK else "Switch to Dark theme"
        )

    def _show_controls_for(self, name: str) -> None:
        try:
            step = self._pipeline.get_step(name)
        except Exception:
            return

        # ── Tear down previous widget ─────────────────────────────────────────
        old = self._controls_container
        if old is not None and hasattr(old, "on_image_processed"):
            try:
                self._controller.image_processed.disconnect(old.on_image_processed)
            except RuntimeError:
                pass

        # ── Disconnect Hough view override from previous widget ───────────────
        if self._hough_override_widget is not None:
            try:
                self._hough_override_widget.view_override.disconnect(
                    self._on_hough_view_override
                )
            except RuntimeError:
                pass
            self._hough_override_widget = None

        # ── Exit crop mode if we were in it ───────────────────────────────────
        if self._crop_step_name is not None:
            self._exit_crop_mode()

        # ── Build new widget ──────────────────────────────────────────────────
        widget = ProcessorControlsRegistry.get_widget(step.processor, parent=self)
        if widget is None:
            widget = QWidget()

        self._controls_scroll.setWidget(widget)
        self._controls_container = widget

        if hasattr(widget, "controls_changed"):
            widget.controls_changed.connect(self._controller.request_update)

        if hasattr(widget, "on_image_processed"):
            self._controller.image_processed.connect(widget.on_image_processed)
            # Immediately refresh previews if pipeline has already run
            if self._last_processed is not None:
                widget.on_image_processed(self._last_processed)

        if hasattr(widget, "view_override"):
            widget.view_override.connect(self._on_hough_view_override)
            self._hough_override_widget = widget

        # ── Enter crop mode if this is a Crop step ────────────────────────────
        if isinstance(step.processor, CropTransformation):
            self._enter_crop_mode(name, widget)

    def _enter_crop_mode(self, step_name: str, widget) -> None:
        from src.ui.widgets.controls.crop_controls import CropControlWidget
        if not isinstance(widget, CropControlWidget):
            return
        self._crop_step_name = step_name
        pre_image = self._controller.get_input_image_for(step_name)
        if pre_image is not None:
            cfg = self._pipeline.get_step(step_name).processor._config
            self._viewer.enter_crop_mode(pre_image, cfg.x, cfg.y, cfg.width, cfg.height)
            self._viewer.fit_in_view()
        # viewer → spinboxes
        self._viewer.crop_rect_changed.connect(widget.set_rect_from_viewer)
        # spinboxes → viewer overlay
        widget.rect_changed_by_ui.connect(self._viewer.update_crop_rect)

    def _exit_crop_mode(self) -> None:
        self._viewer.exit_crop_mode()
        self._crop_step_name = None
        # Immediately restore the last processed result so the viewer doesn't
        # stay stuck on the pre-crop image until the next pipeline run.
        if self._last_processed is not None:
            self._viewer.set_image(self._last_processed)

    def _on_image_processed(self, image) -> None:
        import numpy as np
        self._last_processed = np.ascontiguousarray(image)
        # Reset layer selection — pipeline result is now fresh
        self._viewing_step = None
        self._layers_panel.clear_selection()
        if self._crop_mode_active():
            pre = self._controller.get_input_image_for(self._crop_step_name)
            if pre is not None:
                self._viewer.refresh_crop_image(pre)
        else:
            self._viewer.set_image(image)
        self._histogram.update_image(image)

    def _on_thumbnails_ready(self, thumbnails: dict) -> None:
        step_names = [s.name for s in self._pipeline.steps]
        self._layers_panel.update_layers(step_names, thumbnails)

    def _on_layer_view_requested(self, step_name: str) -> None:
        if not step_name:
            self._viewing_step = None
            if self._last_processed is not None and not self._crop_mode_active():
                self._viewer.set_image(self._last_processed)
            return
        self._viewing_step = step_name
        image = self._controller.get_image_up_to(step_name)
        if image is not None:
            self._viewer.set_image(image)

    def _on_hough_view_override(self, image) -> None:
        if image is not None:
            self._viewer.set_image(image)
        elif self._last_processed is not None and not self._crop_mode_active():
            self._viewer.set_image(self._last_processed)

    def _crop_mode_active(self) -> bool:
        return self._crop_step_name is not None

    def _save_project(self) -> None:
        from src.project import save_project, ProjectFormatError
        if self._controller._original is None:
            QMessageBox.warning(self, "Save Project", "No image loaded.")
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Save project", "", "ImageProcessor Project (*.iproj)"
        )
        if not path:
            return
        if not path.endswith(".iproj"):
            path += ".iproj"
        try:
            save_project(path, self._pipeline.steps, self._controller._original)
        except OSError as exc:
            QMessageBox.critical(self, "Save Project", f"Failed to save:\n{exc}")

    def _open_project(self) -> None:
        import warnings
        from src.project import (
            load_project, ProjectFormatError, ProjectVersionError,
        )
        path, _ = QFileDialog.getOpenFileName(
            self, "Open project", "", "ImageProcessor Project (*.iproj)"
        )
        if not path:
            return
        try:
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter("always")
                step_tuples, original = load_project(path)
        except (ProjectFormatError, ProjectVersionError) as exc:
            QMessageBox.critical(self, "Open Project", f"Cannot open project:\n{exc}")
            return

        if caught:
            msg = "\n".join(str(w.message) for w in caught)
            QMessageBox.warning(self, "Open Project — Warnings", msg)

        self._pipeline.clear()
        for name, processor, enabled in step_tuples:
            self._pipeline.add_step(name, processor, enabled)

        self._controller.set_image(original)
        self._pipeline_panel.refresh()
